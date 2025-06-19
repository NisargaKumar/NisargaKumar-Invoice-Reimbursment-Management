from fastapi import APIRouter, UploadFile, File, Form
import shutil, os, uuid, json
from app.utils.extractors import extract_name, extract_date
from app.utils.prompts import invoice_system_prompt
from app.utils.vector_store import store_analysis
from app.utils.pdf_utils import extract_text_from_pdf
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from app.utils.json_utils import extract_json_from_llm_response

analyze_router = APIRouter()

@analyze_router.post("/upload")
async def analyze_upload(
    policy: UploadFile = File(...),
    invoice_zips: list[UploadFile] = File(...),
    employee_name: str = Form("Unknown")
):
    temp_dir = os.path.join("temp", str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    results = []

    try:
        # Save policy
        policy_path = os.path.join(temp_dir, policy.filename)
        with open(policy_path, "wb") as f:
            f.write(await policy.read())

        policy_text = extract_text_from_pdf(policy_path)
        print("🧾 Policy Extracted Text:\n", policy_text)


        # Unpack invoices
        for z in invoice_zips:
            zpath = os.path.join(temp_dir, z.filename)
            with open(zpath, "wb") as f:
                f.write(await z.read())
            shutil.unpack_archive(zpath, temp_dir)

        from glob import glob
        pdfs = glob(os.path.join(temp_dir, "**/*.pdf"), recursive=True)
        pdfs = [pdf for pdf in pdfs if os.path.basename(pdf) != os.path.basename(policy_path)]
        # Initialize LLaMA model via Groq
        llm = ChatGroq(model_name="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))

        for pdf in pdfs:
            try:
                txt = extract_text_from_pdf(pdf)
                name = employee_name if employee_name.lower() != "unknown" else extract_name(txt)
                date = extract_date(txt)

                messages = [
                    SystemMessage(content="""
                    You are an AI assistant reviewing company expense invoices for reimbursement. Each invoice may contain travel, meal, accommodation, or miscellaneous expenses. Your job is to:

                    1. Extract key details: employee name (if available), date (if available), and expense type with amounts.
                    2. Analyze based on strict company reimbursement policy.
                    3. Output a single structured JSON object with accurate status and a **clear reason that includes math comparisons**.
                    4. Do NOT leave "reason" blank — ever.
                    5. If a name or date is missing, set them to "Unknown".

                    ------------------------
                    🎯 COMPANY POLICY
                    ------------------------

                    ✅ FULLY REIMBURSED:
                    - Cab fare: ≤ ₹150 per ride
                    - Meals: ≤ ₹200 per meal (no alcohol)
                    - Flights: ≤ ₹2000 (must be work-related)
                    - Hotel/Stay: Must be for business trip and reasonable
                    - CGST/SGST: Reimbursed only if explicitly allowed or mentioned

                    🟡 PARTIALLY REIMBURSED:
                    - Amount exceeds limit but invoice is valid
                    - Missing info (e.g., name/date), but content is work-related
                    - Only some items are eligible (e.g., food ok, alcohol not)

                    ❌ DECLINED:
                    - Alcohol (e.g., whisky, wine, beer)
                    - Personal or leisure travel
                    - Invalid/incomplete invoices
                    - No pricing info or total unclear

                    ------------------------
                    ⚠️ SPECIAL RULES
                    ------------------------
                    - Always explain the math. Example: “Cab fare ₹167 exceeds ₹150 limit — reimbursed up to ₹150.”
                    - Never say something is within the limit if it's not.
                    - If item is alcohol or personal, say so clearly.
                    - If invoice includes taxes like CGST/SGST, include them only if allowed.

                    ------------------------
                    🧾 RESPONSE FORMAT (strict JSON only)
                    ------------------------

                    {
                    "status": "Fully Reimbursed" | "Partially Reimbursed" | "Declined",
                    "reason": "Explain exactly why, with math where relevant.",
                    "employee": "Name or 'Unknown'",
                    "date": "YYYY-MM-DD or 'Unknown'"
                    }

                    ------------------------
                    💡 EXAMPLES
                    ------------------------

                    - "Cab fare ₹132"  
                    → `status: "Fully Reimbursed", reason: "Cab fare ₹132 is within ₹150 daily limit."`

                    - "Cab fare ₹167"  
                    → `status: "Partially Reimbursed", reason: "Cab fare ₹167 exceeds ₹150 limit — reimbursed up to ₹150."`

                    - "Meal ₹450 with whisky"  
                    → `status: "Declined", reason: "Includes alcohol (whisky), which is not reimbursable."`

                    - "Flight ₹6251 for work"  
                    → `status: "Partially Reimbursed", reason: "Flight cost ₹6251 exceeds ₹2000 limit for work travel."`

                    - "Food ₹180, no name"  
                    → `status: "Fully Reimbursed", reason: "Meal ₹180 is within limit. Employee name missing.", employee: "Unknown"`

                    ------------------------
                    🔍 TASK
                    ------------------------

                    You will receive an extracted invoice text from a PDF file. Analyze it as per the above policy and return **only the final JSON** — no explanations, no formatting, no markdown.

                    """),
                    
                    HumanMessage(content=f"Policy:\n{policy_text}\n\nInvoice:\n{txt}")
                ]

                resp = llm(messages)

                llm_output = extract_json_from_llm_response(resp.content)
                if "error" in llm_output:
                    results.append({"invoice": os.path.basename(pdf), "error": llm_output["error"]})
                    continue

                llm_output.setdefault("employee", name)
                llm_output.setdefault("date", date)

                store_analysis(txt, llm_output, pdf)
                results.append({"invoice": os.path.basename(pdf), **llm_output})

            except Exception as e:
                results.append({"invoice": os.path.basename(pdf), "error": str(e)})


        return {"status": "success", "results": results}

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
