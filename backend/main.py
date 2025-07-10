# backend/main.py
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from assistant import get_response  # function defined in assistant.py

app = FastAPI()

# Allow requests from React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    products: list[dict] = []
    session_id: str

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Generate new session_id if not provided
    sid = req.session_id or str(uuid.uuid4())
    # Call assistant get_response
    result = get_response(req.message, sid)
    # result expected to be dict with keys: response, products, session_id
    return result
