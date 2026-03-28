import uuid
from datetime import datetime, timezone
from src.openai_agent import OpenAIAgent


class OpenAIAgentExecutor:
    """
    Handles A2A JSON-RPC 2.0 requests from the Nasiko gateway and returns
    fully structured, spec-compliant responses.
    """

    def __init__(self):
        self.agent = OpenAIAgent()

    # ── Main executor ─────────────────────────────────────────────────────────
    async def execute(self, request: dict) -> dict:
        """
        Process an incoming A2A request and return a gateway-compliant response.

        Expected request shape:
        {
          "jsonrpc": "2.0",
          "id": "<request-id>",
          "method": "tasks/send",
          "params": {
            "id": "<task-id>",
            "message": {
              "role": "user",
              "parts": [{ "kind": "text", "text": "<user message>" }]
            }
          }
        }

        Returns:
            A2A JSON-RPC 2.0 result object.
        """
        request_id = request.get("id", str(uuid.uuid4()))

        try:
            # ── Extract user message ──────────────────────────────────────────
            user_message = self._extract_message(request)

            # ── Run the agent ─────────────────────────────────────────────────
            response_text = await self.agent.run(user_message)

            # ── Build compliant response ──────────────────────────────────────
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "id"        : request.get("params", {}).get("id", str(uuid.uuid4())),
                    "contextId" : str(uuid.uuid4()),
                    "kind"      : "task",
                    "status": {
                        "state"    : "completed",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    "artifacts": [
                        {
                            "artifactId": str(uuid.uuid4()),
                            "name"      : "alpha_quant_response",
                            "parts"     : [
                                {
                                    "kind": "text",
                                    "text": response_text,
                                }
                            ],
                        }
                    ],
                },
            }

        except Exception as e:
            return self._error_response(request_id, -32000, f"Execution error: {str(e)}")

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _extract_message(request: dict) -> str:
        """Safely extract the user text from the A2A request params."""
        try:
            parts = request["params"]["message"]["parts"]
            # Concatenate all text parts
            texts = [p["text"] for p in parts if p.get("kind") == "text" and "text" in p]
            if not texts:
                raise ValueError("No text parts found in message.")
            return " ".join(texts)
        except (KeyError, TypeError, IndexError) as exc:
            raise ValueError(f"Malformed A2A request — could not extract message: {exc}") from exc

    @staticmethod
    def _error_response(request_id: str, code: int, message: str) -> dict:
        """Return a JSON-RPC 2.0 error envelope."""
        return {
            "jsonrpc": "2.0",
            "id"     : request_id,
            "error"  : {
                "code"   : code,
                "message": message,
                "data"   : {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            },
        }