import requests


class LlamaGenerator:
    """
    Generate text using Ollama/Llama 3.2 3B locally.
    Assumes Ollama is running on http://localhost:11434
    """
    
    def __init__(self, model="llama2", ollama_url="http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
    
    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text from the model
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama: {str(e)}")


def create_qa_prompt(context: str, question: str) -> str:
    """
    Create a prompt for Q&A based on retrieved context.
    
    Args:
        context: Retrieved context from vector store
        question: User's question
        
    Returns:
        Formatted prompt
    """
    return f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""