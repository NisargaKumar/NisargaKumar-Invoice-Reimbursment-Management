import os
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from app.utils.prompts import analysis_prompt, chatbot_prompt

groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(api_key=groq_api_key, model_name="llama3-8b-8192")

def analyze_invoice_with_llm(invoice: str, policy: str) -> str:
    messages = [
        SystemMessage(content=analysis_prompt),
        HumanMessage(content=f"Policy:\n{policy}\n\nInvoice:\n{invoice}")
    ]
    return llm(messages).content

def answer_with_context(query: str, docs: list) -> str:
    context = "\n\n".join([d.page_content for d in docs])
    messages = [
        SystemMessage(content=chatbot_prompt),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion:\n{query}")
    ]
    return llm(messages).content

