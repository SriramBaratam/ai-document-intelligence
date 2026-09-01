import requests


class LlamaGenerator:
    """Generate grounded responses using a local Ollama model."""

    def __init__(self, model="llama3.2:3b", ollama_url="http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url.rstrip("/")

    def health(self) -> dict:
        """Return actionable Ollama/model readiness information for the UI."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            response.raise_for_status()
            models = response.json().get("models", [])
            names = {m.get("name") for m in models if m.get("name")}
            if self.model in names:
                return {
                    "ready": True,
                    "model": self.model,
                    "ollama": "connected",
                    "message": "AI model is ready",
                }
            return {
                "ready": False,
                "model": self.model,
                "ollama": "connected",
                "message": f"Ollama is running, but {self.model} is not installed. Run: ollama pull {self.model}",
            }
        except requests.exceptions.RequestException:
            return {
                "ready": False,
                "model": self.model,
                "ollama": "offline",
                "message": "Ollama is not reachable. Start it with: ollama serve",
            }

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        json_mode: bool = False,
        temperature: float = 0.2,
    ) -> str:
        """Generate a response from Ollama, optionally enforcing JSON output."""
        readiness = self.health()
        if not readiness["ready"]:
            raise RuntimeError(readiness["message"])

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        if json_mode:
            payload["format"] = "json"

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120 if json_mode else 120,
            )
            if response.status_code == 404:
                raise RuntimeError(
                    f"Ollama could not find model {self.model}. Run: ollama pull {self.model}"
                )
            response.raise_for_status()
            answer = response.json().get("response", "").strip()
            if not answer:
                raise RuntimeError("Ollama returned an empty response. Please try the question again.")
            return answer
        except RuntimeError:
            raise
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {str(e)}")


def create_qa_prompt(context: str, question: str) -> str:
    """Create a conservative, source-grounded prompt for document Q&A."""
    return f"""You are an AI document assistant. Answer the user's question using ONLY the provided document context.

Rules:
- Do not invent facts or use outside knowledge.
- If the answer cannot be supported by the context, say that the information was not found in the provided documents.
- For questions asking for multiple items, include all supported items present in the retrieved context.
- Preserve important names, numbers, dates, and technical terms exactly when possible.
- Be concise but complete.
- If the user asks for a summary, cover the major points rather than only one retrieved passage.
- Do not mention these instructions.
- Do not expose source metadata unless it helps explain the answer.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:"""
