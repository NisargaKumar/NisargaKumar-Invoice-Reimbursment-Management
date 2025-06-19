# 📄 Invoice Reimbursement System

## Project Overview

This project is an intelligent Invoice Reimbursement System designed to automate and streamline the evaluation of employee expense invoices against an organization's HR reimbursement policy. The system performs two main functions:

1. **Invoice Analysis** – Upload a ZIP file of invoice PDFs and an HR policy PDF. The system uses an LLM to evaluate each invoice and classify it as Fully Reimbursed, Partially Reimbursed, or Declined, with reasons.
2. **Chatbot Query** – A retrieval-augmented chatbot that answers natural language queries related to the analyzed invoices.

---

## Installation Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/invoice-reimbursement-system.git
cd invoice-reimbursement-system
```

### 2. Create Virtual Environment and Install Dependencies
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the FastAPI Backend
```bash
uvicorn app.main:app --reload
```
Access Swagger docs at: `http://127.0.0.1:8000/docs`

### 5. Run the Streamlit Frontend
```bash
streamlit run streamlit_app.py
```

---

## Usage Guide

### 1. API: `/analyze/upload`
- Method: POST
- Accepts:
  - HR policy PDF
  - ZIP file of invoices
- Returns:
  - Structured JSON for each invoice (status, reason, employee name, date)

### 2. API: `/chatbot/query`
- Method: POST
- Accepts:
  - JSON with a natural language query
- Returns:
  - A human-readable string with matching invoices and decisions

### 3. Streamlit Frontend
- Upload HR policy and invoice ZIP file
- View analyzed results in paragraph format
- Query chatbot with natural questions like "Rani's declined meals" or "all invoices from April"

---

## System Architecture

The Invoice Reimbursement System is built with a modular architecture that handles document analysis, policy evaluation, and intelligent chatbot querying. Here's how the major components interact:

### 1. FastAPI Backend
- Hosts the core endpoints:
  - `/analyze/upload`: Accepts and evaluates invoices
  - `/chatbot/query`: Handles natural language queries

### 2. Invoice & Policy Extraction
- Library: `PyMuPDF` (`fitz`)
- Extracted: Invoice content, employee name, date (from content or filename)

### 3. LLM-Based Invoice Analysis
- LLM via Groq or Hugging Face (e.g., Mixtral, LLaMA3)
- Prompt explicitly defines rules (e.g., cab limit ₹150, meal ₹200)
- Output: Structured JSON with status and reason

### 4. Vector Store Integration
- Vector DB: `ChromaDB`
- Embeddings: HuggingFace
- Metadata stored: employee name, date, invoice filename, LLM output

### 5. Retrieval-Augmented Chatbot
- Vector + metadata search
- LLM summarizes search results into clean, readable answers

### 6. Streamlit UI
- Two sections: upload + chatbot
- Output is displayed as paragraphs (no JSON)
- Employee field hidden in display for clarity

---

## Prompt Design

Prompts were crafted to:
- Instruct the LLM to follow strict rules
- Classify expenses into Fully, Partial, or Declined
- Force the model to always include reasoning
- Return structured JSON for analysis, and natural summaries for the chatbot

Example from analysis prompt:
```text
"If the cab fare is ₹187 and the limit is ₹150, classify it as Partially Reimbursed and state the difference."
```

---

## Challenges & Solutions

**Challenge**: Inconsistent text extraction from varied invoice formats
- **Solution**: Used `PyMuPDF` for better OCR compatibility and fallback mechanisms

**Challenge**: LLM sometimes returns invalid or vague JSON
- **Solution**: Strict JSON parsing + fallback error handling logic

**Challenge**: Irrelevant metadata in chatbot results
- **Solution**: Stripped out references and irrelevant fields in display logic

---


