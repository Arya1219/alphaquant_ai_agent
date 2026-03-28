import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.openai_agent_executor import OpenAIAgentExecutor

app = FastAPI(
    title="AlphaQuant — Impulse Flow Alpha Agent",
    description="Nasiko A2A-compliant AI agent for quantitative trading strategy analysis.",
    version="1.0.0",
)

executor = OpenAIAgentExecutor()


# ── A2A gateway endpoint ──────────────────────────────────────────────────────
@app.post("/")
async def handle_a2a(request: Request):
    """
    Main A2A JSON-RPC 2.0 endpoint consumed by the Nasiko gateway.
    """
    body = await request.json()
    response = await executor.execute(body)
    return JSONResponse(content=response)


# ── Agent card ────────────────────────────────────────────────────────────────
@app.get("/.well-known/agent.json")
async def agent_card():
    """
    Serve the AgentCard so the Nasiko registry can discover this agent.
    """
    import json, pathlib
    card_path = pathlib.Path(__file__).parent.parent / "AgentCard.json"
    if card_path.exists():
        return JSONResponse(content=json.loads(card_path.read_text()))
    return JSONResponse(content={"error": "AgentCard.json not found"}, status_code=404)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "agent": "AlphaQuant"}


# ── Local dev runner ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("src.__main__:app", host="0.0.0.0", port=10000, reload=True)