import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []

    def add(self, embeddings, documents):
        vectors = np.asarray(embeddings, dtype="float32")

        self.index.add(vectors)
        self.documents.extend(documents)

    def search(self, query_embedding, top_k=3):
        query_vector = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_vector,
            top_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index != -1:
                results.append({
                    "document": self.documents[index],
                    "score": float(score),
                })

        return results