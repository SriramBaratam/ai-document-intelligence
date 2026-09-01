import requests


class LlamaGenerator:
    """Generate grounded responses using a local Ollama model."""

    def __init__(self, model="llama3.2:3b", ollama_url="http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.2},
                },
                timeout=60,
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