import os
import io
import json
import csv
from openai import OpenAI
from src.agent_toolset import QuantTradingToolset


SYSTEM_PROMPT = """
You are AlphaQuant, a professional AI agent specialising in quantitative trading
strategy analysis. You are deployed on the Nasiko A2A gateway.

Your capabilities:
  1. explain_strategy    - Explain the Impulse Flow Alpha trading strategy clearly.
  2. analyze_performance - Interpret backtest metrics (return, Sharpe, drawdown, etc.).
  3. evaluate_risk       - Summarise stress tests and forward-looking risks.
  4. generate_signal     - Run the signal engine on provided OHLC data (5+ bars).
  5. run_backtest        - Run the full backtest on a complete OHLC dataset and
                           return all performance metrics computed live.

Response guidelines:
  - Always reply in a clear, structured format.
  - Be precise, analytical, and professional.
  - Do NOT hype unrealistic returns; always mention risks and limitations.
  - If the user provides OHLC data as JSON or CSV, detect whether they want a
    single signal (few bars) or a full backtest (many bars / keyword backtest).
  - Keep outputs deterministic and consistent for the same input.
  - If a request is outside your five capabilities, politely say so and suggest
    which capability is closest.
"""

# Minimum bars to auto-escalate generate_signal -> run_backtest
_BACKTEST_BAR_THRESHOLD = 30


class OpenAIAgent:
    """
    Wraps the OpenAI chat API with tool routing via QuantTradingToolset.
    Falls back to a pure LLM response when no tool matches.
    """

    def __init__(self):
        self.client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.toolset = QuantTradingToolset()

    # ── Intent detection ──────────────────────────────────────────────────────
    @staticmethod
    def _detect_intent(text: str):
        """
        Keyword-based intent router evaluated in priority order.
        Returns one of the tool keys or None (-> fallback to LLM).
        """
        t = text.lower()

        # run_backtest checked BEFORE generate_signal / performance
        if any(k in t for k in ["backtest", "run backtest", "full backtest",
                                 "test this data", "simulate", "back test"]):
            return "run_backtest"

        if any(k in t for k in ["explain", "how does", "what is impulse",
                                 "what is the strategy", "describe strategy"]):
            return "explain_strategy"

        if any(k in t for k in ["performance", "metrics", "sharpe", "sortino",
                                 "calmar", "annualised", "drawdown"]):
            return "analyze_performance"

        if any(k in t for k in ["risk", "stress", "robust", "overfitting",
                                 "monte carlo", "perturbation"]):
            return "evaluate_risk"

        if any(k in t for k in ["signal", "generate signal", "ohlc",
                                 "predict", "trade now", "go long", "go short"]):
            return "generate_signal"

        return None

    # ── Main entry point ──────────────────────────────────────────────────────
    async def run(self, user_input: str) -> str:
        """
        Route request to the appropriate tool or fall back to the LLM.

        Args:
            user_input: Raw user message text.

        Returns:
            Response string.
        """
        try:
            intent = self._detect_intent(user_input)
            tools  = self.toolset.get_tools()

            if intent and intent in tools:

                if intent == "explain_strategy":
                    return await tools["explain_strategy"](strategy_text=user_input)

                if intent == "analyze_performance":
                    return await tools["analyze_performance"]()

                if intent == "evaluate_risk":
                    return await tools["evaluate_risk"]()

                if intent == "run_backtest":
                    rows = self._extract_ohlc(user_input)
                    if rows:
                        return await tools["run_backtest"](csv_rows=rows)
                    return (
                        "To run a full backtest I need OHLC data.\n"
                        "Please provide either:\n"
                        '  (a) A JSON array:  [{"Date":"2020-01-01","Open":7200,'
                        '"High":7400,"Low":7100,"Close":7350}, ...]\n'
                        "  (b) CSV text with header row: Date,Open,High,Low,Close\n\n"
                        "At least 10 bars are required."
                    )

                if intent == "generate_signal":
                    rows = self._extract_ohlc(user_input)
                    if rows:
                        if len(rows) >= _BACKTEST_BAR_THRESHOLD:
                            return await tools["run_backtest"](csv_rows=rows)
                        return await tools["generate_signal"](ohlc_data=rows)
                    return (
                        "To generate a signal I need OHLC data.\n"
                        "Please provide a JSON array like:\n"
                        '  [{"Date":"2024-01-01","Open":42000,"High":43000,'
                        '"Low":41500,"Close":42800}, ...]\n'
                        "At least 5 bars are required.\n"
                        "For a full backtest (30+ bars) use the keyword 'backtest'."
                    )

            # ── LLM fallback ──────────────────────────────────────────────────
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_input},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error in AlphaQuant agent: {str(e)}"

    # ── Helper: extract OHLC from JSON array or CSV text ─────────────────────
    @staticmethod
    def _extract_ohlc(text: str):
        """
        Parse OHLC rows from user message.
        Supports:
          1. JSON array  - [...] anywhere in the text.
          2. CSV block   - lines with commas and a Date,Open,High,Low,Close header.

        Returns a list of dicts on success, None on failure.
        """
        # Try JSON first
        try:
            start  = text.index("[")
            end    = text.rindex("]") + 1
            parsed = json.loads(text[start:end])
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except (ValueError, json.JSONDecodeError):
            pass

        # Try CSV block
        try:
            csv_lines = [
                line.strip()
                for line in text.splitlines()
                if "," in line and line.strip()
            ]
            if len(csv_lines) < 2:
                return None

            reader = csv.DictReader(io.StringIO("\n".join(csv_lines)))
            rows   = [row for row in reader]

            if not rows:
                return None

            first_keys = {k.strip().lower() for k in rows[0].keys()}
            required   = {"date", "open", "high", "low", "close"}
            if not required.issubset(first_keys):
                return None

            key_map = {k: k.strip().title() for k in rows[0].keys()}
            return [{key_map[k]: v for k, v in row.items()} for row in rows]

        except Exception:
            return None
