# ==========================================
# Tool Name: Beko Ai Api (Production Edition)
# Version: V1.1
# Developer: Mubarak Azzoz (OadAlBragna)
# Portfolio: https://mubarak.zone.id
# Website: https://oadalbragna.blogspot.com
# Description: Professional Grade AI API - No API Keys Needed.
# ==========================================

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
import g4f
import asyncio
import threading
import uvicorn
import uuid

# --- Engine Configuration ---
class AIModelEngine:
    def __init__(self):
        self.client = g4f.client.AsyncClient()
        self.loop = asyncio.new_event_loop()
        self.ready = threading.Event()
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.ready.set()
        self.loop.run_forever()

    async def _generate(self, prompt: str):
        response = await self.client.chat.completions.create(
            model=g4f.models.gpt_4o_mini,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def process(self, prompt: str):
        if not self.ready.wait(timeout=10):
            raise Exception("AI Engine not ready")
        future = asyncio.run_coroutine_threadsafe(self._generate(prompt), self.loop)
        return future.result(timeout=120)

engine = AIModelEngine()

# --- FastAPI Setup ---
app = FastAPI(title="Beko Ai Api", version="1.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Endpoints ---
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        data = await request.json()
        messages = data.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        prompt = messages[-1].get("content", "")
        response_text = engine.process(prompt)
        
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
            "object": "chat.completion",
            "created": int(import_time := __import__('time').time()),
            "model": "gpt-4o-mini",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": response_text}, "finish_reason": "stop"}]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth")
async def auth_check():
    return {"status": "authenticated", "message": "Beko Ai Api is online."}

@app.get("/api")
async def api_proxy(chat: str = Query(...)):
    try:
        response = engine.process(chat)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7777)
