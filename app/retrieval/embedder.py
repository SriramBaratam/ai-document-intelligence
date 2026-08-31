from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        """
        Convert text into numerical embeddings.

        Args:
            texts: A single string or a list of strings.

        Returns:
            Embedding vectors.
        """
        return self.model.encode(
            texts,
            normalize_embeddings=True
        )