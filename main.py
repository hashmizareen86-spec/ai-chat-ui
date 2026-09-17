import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GenAI Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace your Gemini API Key directly
GEMINI_API_KEY = "GEMINI_API_KEY"

client = genai.Client(api_key=GEMINI_API_KEY)
class ChatRequest(BaseModel):
    prompt: str
    model: str = "gemini-2.5-flash"

async def generate_stream(prompt: str, model_name: str):
    try:
        response = client.models.generate_content_stream(
            model=model_name,
            contents=prompt
        )
        for chunk in response:
            if chunk.text:
                yield f"data: {chunk.text}\n\n"
                await asyncio.sleep(0.01)
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        generate_stream(request.prompt, request.model),
        media_type="text/event-stream"
    )