from fastapi import FastAPI
from app.routers.analyze import analyze_router
from app.routers.chatbot import chatbot_router

app = FastAPI(title="Invoice Reimbursement System")

# Register the routers with correct names
app.include_router(analyze_router, prefix="/analyze", tags=["Invoice Analysis"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot Query"])
