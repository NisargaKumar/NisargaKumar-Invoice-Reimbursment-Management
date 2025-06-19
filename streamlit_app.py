import streamlit as st
import requests
import re

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Invoice Reimbursement System", layout="wide")
st.title("📄 Invoice Reimbursement System")

# ----------------------- Upload Section -----------------------
st.header("🔍 Analyze Invoices")

policy_file = st.file_uploader("Upload HR Policy PDF", type=["pdf"])
invoice_zip = st.file_uploader("Upload Invoices (ZIP)", type=["zip"])

if st.button("Submit for Analysis", type="primary"):
    if policy_file and invoice_zip:
        with st.spinner("Analyzing invoices..."):
            files = {
                "policy": policy_file,
                "invoice_zips": invoice_zip,
            }

            res = requests.post(f"{BACKEND_URL}/analyze/upload", files=files)

            if res.status_code == 200:
                st.success("✅ Analysis complete!")
                results = res.json().get("results", [])

                for result in results:
                    st.markdown("---")
                    invoice = result.get("invoice", "Unknown")
                    employee = result.get("employee", "Unknown")
                    date = result.get("date", "Unknown")
                    status = result.get("status", "Unknown")
                    reason = result.get("reason", "No reason provided.")

                    paragraph = (
                        f"📄 **Invoice:** {invoice}\n\n"
                        f"👤 **Employee:** {employee}\n\n"
                        f"🗓️ **Date:** {date}\n\n"
                        f"📝 **Status:** {status}\n\n"
                        f"🔍 **Reason:** {reason}"
                    )
                    st.markdown(paragraph)

            else:
                st.error("❌ Failed to analyze. Check server or file inputs.")
    else:
        st.warning("Please upload both policy and invoice ZIP files.")

# ----------------------- Chatbot Section -----------------------
st.header("💬 Reimbursement Chatbot")

user_query = st.text_input("Ask something like: Rani's invoices, declined meals, etc.")

if st.button("Ask", key="chat"):
    if user_query.strip():
        with st.spinner("Thinking..."):
            payload = {"query": user_query}
            res = requests.post(f"{BACKEND_URL}/chatbot/query", json=payload)

            if res.status_code == 200:
                full_response = res.json().get("response", "No response.")
                clean_response = re.sub(r"\n\nReference:.*", "", full_response, flags=re.DOTALL)
                st.markdown(clean_response)
            else:
                st.error("❌ Query failed.")
    else:
        st.warning("Please enter a question.")
