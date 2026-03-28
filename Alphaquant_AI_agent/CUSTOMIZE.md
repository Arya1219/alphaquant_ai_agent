# Customisation Guide

## Changing Strategy Parameters

All thresholds live at the top of `src/agent_toolset.py`:

```python
IMPULSE_MIN_LONG   = 0.0013   # min impulse bar return for long
IMPULSE_MAX_LONG   = 0.0027
BREAKOUT_MIN_LONG  = 0.019
BREAKOUT_MAX_LONG  = 0.05
RETRACE_MAX_LONG   = 0.03
# ... short params below
WINDOW_THRESHOLD   = 40       # lookback bars
TCS                = 0.0015   # transaction cost
```

## Adding a New Tool

1. Add an `async def my_tool(self, ...) -> str` method to `QuantTradingToolset`.
2. Register it in `get_tools()`.
3. Add a keyword to `OpenAIAgent._detect_intent()`.
4. Add a skill entry to `AgentCard.json`.

## Switching LLM Provider

Replace the `OpenAI` client in `src/openai_agent.py` with any provider that
exposes a compatible `.chat.completions.create()` interface (e.g. Anthropic via
the `anthropic` SDK, or a local Ollama endpoint).
