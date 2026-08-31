def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks.

    Args:
        text: The input text.
        chunk_size: Maximum number of characters in each chunk.
        overlap: Number of characters shared between consecutive chunks.

    Returns:
        A list of text chunks.
    """

    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks