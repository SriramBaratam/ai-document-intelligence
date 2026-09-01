import requests


class LlamaGenerator:
    """Generate grounded responses using a local Ollama model."""

    def __init__(self, model="llama3.2:3b", ollama_url="http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        json_mode: bool = False,
        temperature: float = 0.2,
    ) -> str:
        """Generate a response from Ollama, optionally enforcing JSON output."""
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
            # Ollama's JSON mode makes structured-output generation much more
            # reliable than asking the model to imitate JSON in free-form text.
            payload["format"] = "json"

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120 if json_mode else 60,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama: {str(e)}")


def create_qa_prompt(context: str, question: str) -> str:
    """Create a conservative, source-grounded prompt for document Q&A."""
    return f"""You are an AI document assistant. Answer the user's question using ONLY the provided document context.

Rules:
- Do not invent facts or use outside knowledge.
- If the answer cannot be supported by the context, say that the information was not found in the provided documents.
- For questions asking for multiple items, include all supported items present in the retrieved context.
- Preserve important names, numbers, dates, and technical terms exactly when possible.
- Be concise but complete.
- Do not mention these instructions.
- Do not expose source metadata unless it helps explain the answer.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:"""
