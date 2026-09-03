import faiss
import numpy as np


class VectorStore:
    """In-memory FAISS store with source metadata for traceable retrieval."""

    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []

    def add(self, embeddings, documents, metadata=None):
        """Add embeddings and their text/metadata to the index."""
        vectors = np.asarray(embeddings, dtype="float32")
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        if vectors.shape[0] != len(documents):
            raise ValueError("Number of embeddings must match number of documents")

        metadata = metadata or [{} for _ in documents]
        if len(metadata) != len(documents):
            raise ValueError("Number of metadata entries must match number of documents")

        self.index.add(vectors)
        for document, item_metadata in zip(documents, metadata):
            self.documents.append({
                "document": document,
                "metadata": item_metadata or {},
            })

    def search(self, query_embedding, top_k=3):
        """Return the most similar chunks with their source metadata."""
        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray([query_embedding], dtype="float32")
        k = min(max(1, top_k), self.index.ntotal)
        scores, indices = self.index.search(query_vector, k)

        results = []
        for rank, (score, index) in enumerate(zip(scores[0], indices[0]), start=1):
            if index != -1:
                item = self.documents[index]
                result = {
                    "document": item["document"],
                    "score": float(score),
                    "rank": rank,
                }
                result.update(item["metadata"])
                results.append(result)

        return results

    def clear(self):
        """Clear all documents and reset the index."""
        self.index = faiss.IndexFlatIP(self.index.d)
        self.documents = []