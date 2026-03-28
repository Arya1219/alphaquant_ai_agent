# AlphaQuant — Impulse Flow Alpha Agent
**Nasiko A2A AI Hackathon | Team GenAlpha | IIT BHU Varanasi**

An A2A-compliant AI agent that analyses the **Impulse Flow Alpha** quantitative
trading strategy on BTC-USDT daily data.

---

## Capabilities

| Skill | Description |
|---|---|
| `explain_strategy` | Plain-English explanation of the Impulse → Consolidation → Breakout pattern |
| `analyze_performance` | Interpret backtest metrics (return, Sharpe, Sortino, Calmar, drawdown) |
| `evaluate_risk` | Summarise all four stress tests + forward-looking risks |
| `generate_signal` | Run the live signal engine on user-supplied OHLC data |

---

## Quick Start (one command)

```bash
OPENAI_API_KEY=sk-... docker compose up --build
```

The agent is now live at `http://localhost:10000`.

---

## File Structure

```
.
├── src/
│   ├── __init__.py
│   ├── __main__.py            # FastAPI app + A2A endpoint
│   ├── agent_toolset.py       # All four tool implementations
│   ├── openai_agent.py        # Intent routing + OpenAI fallback
│   └── openai_agent_executor.py  # A2A JSON-RPC 2.0 wrapper
├── AgentCard.json             # Nasiko registry metadata
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Sample A2A Request & Response

### Request
```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "method": "tasks/send",
  "params": {
    "id": "task-001",
    "message": {
      "role": "user",
      "parts": [{ "kind": "text", "text": "Explain the Impulse Flow Alpha strategy." }]
    }
  }
}
```

### Response
```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "id": "task-001",
    "contextId": "<uuid>",
    "kind": "task",
    "status": {
      "state": "completed",
      "timestamp": "2026-03-28T10:00:00+00:00"
    },
    "artifacts": [{
      "artifactId": "<uuid>",
      "name": "alpha_quant_response",
      "parts": [{
        "kind": "text",
        "text": "=== Impulse Flow Alpha — Strategy Explanation ===\n..."
      }]
    }]
  }
}
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key |

---

## Local Dev (without Docker)

```bash
pip install -e .
export OPENAI_API_KEY=sk-...
python -m src
```
