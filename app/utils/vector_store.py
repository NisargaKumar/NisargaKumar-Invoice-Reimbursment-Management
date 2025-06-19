import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()
collection = client.get_or_create_collection("invoices")
emb_model = SentenceTransformer("all-MiniLM-L6-v2")

def store_analysis(invoice_text, llm_output: dict, invoice_path: str):
    full_text = f"Invoice: {invoice_path}\nStatus: {llm_output['status']}\nReason: {llm_output['reason']}\nEmployee: {llm_output.get('employee')}\nDate: {llm_output.get('date')}\n\n{invoice_text}"
    embedding = emb_model.encode(full_text).tolist()
    collection.add(
        documents=[full_text],
        embeddings=[embedding],
        metadatas=[{
            "invoice": invoice_path,
            "status": llm_output["status"],
            "reason": llm_output["reason"],
            "employee": llm_output.get("employee", "Unknown"),
            "date": llm_output.get("date", "Unknown")
        }],
        ids=[invoice_path]
    )

def query_invoices(query_text: str, filters: dict = None, top_k=10):
    query_emb = emb_model.encode(query_text).tolist()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        where=filters if filters else None
    )
    return [
        {
            "invoice": results["metadatas"][0][i]["invoice"],
            "employee": results["metadatas"][0][i]["employee"],
            "date": results["metadatas"][0][i]["date"],
            "status": results["metadatas"][0][i]["status"],
            "reason": results["metadatas"][0][i]["reason"],
            "doc": results["documents"][0][i]
        }
        for i in range(len(results["ids"][0]))
    ]
