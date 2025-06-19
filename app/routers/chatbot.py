from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.vector_store import query_invoices
from app.utils.prompts import chatbot_system_prompt
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import os

chatbot_router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@chatbot_router.post("/query")
async def chatbot_query(req: QueryRequest):
    filters = {}
    parts = req.query.split()
    if "for" in parts:
        idx = parts.index("for")
        if idx + 1 < len(parts):
            filters["employee"] = parts[idx + 1]

    docs = query_invoices(req.query, filters)
    
    # Clean invoice names for context (only filenames)
    cleaned_docs_texts = []
    for d in docs:
        filename = os.path.basename(d["invoice"])
        # You can customize what you want to send to LLM here
        cleaned_docs_texts.append(
            f"Invoice: {filename}\nStatus: {d['status']}\nReason: {d.get('reason', 'N/A')}\nEmployee: {d.get('employee', 'Unknown')}\nDate: {d.get('date', 'Unknown')}\n"
        )
    content = "\n\n".join(cleaned_docs_texts)

    llm = ChatGroq(model_name="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))
    messages = [
        SystemMessage(content=chatbot_system_prompt),
        HumanMessage(content=f"Context:\n{content}\n\nQuery:\n{req.query}")
    ]
    resp = llm.invoke(messages)


    return {
        "response": resp.content,
        "matched_invoices": [
            {
                "invoice": os.path.basename(d["invoice"]),  # just filename here
                "employee": d["employee"],
                "date": d["date"],
                "status": d["status"]
            }
            for d in docs
        ]
    }
