import uvicorn
from fastapi import FastAPI, Request
from src.openai_agent_executor import OpenAIAgentExecutor

app = FastAPI(
    title="AlphaQuant — Impulse Flow Alpha Agent",
    description="Nasiko A2A-compliant AI agent for quantitative trading strategy analysis.",
    version="1.0.0",
)

executor = OpenAIAgentExecutor()


@app.post("/")
async def handle_a2a(request: Request):
    body = await request.json()
    response = await executor.execute(body)
    return response


@app.get("/")
async def root():
    return {"status": "running"}


@app.get("/.well-known/agent.json")
async def agent_card():
    import json, pathlib
    card_path = pathlib.Path(__file__).parent.parent / "AgentCard.json"
    if card_path.exists():
        return json.loads(card_path.read_text())
    return {"error": "AgentCard.json not found"}


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "AlphaQuant"}


if __name__ == "__main__":
    uvicorn.run("src.__main__:app", host="0.0.0.0", port=10000)
