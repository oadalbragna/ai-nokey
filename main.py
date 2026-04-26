from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import g4f
import asyncio
import uuid
import time

# --- FastAPI Setup ---
app = FastAPI(title="Beko Ai Api", version="1.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Engine Logic ---
async def generate_response(prompt: str):
    client = g4f.client.AsyncClient()
    response = await client.chat.completions.create(
        model=g4f.models.gpt_4o_mini,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- Endpoints ---
@app.post("/")
async def root_post(request: Request):
    try:
        data = await request.json()
        prompt = data.get("message", "")
        if not prompt:
            raise HTTPException(status_code=400, detail="No message provided")
        
        response_text = await generate_response(prompt)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root_get():
    return {"status": "online", "message": "Beko Ai Api is ready."}
