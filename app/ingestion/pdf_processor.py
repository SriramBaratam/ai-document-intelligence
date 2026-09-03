from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from all PDF pages while preserving page markers."""
    pages = extract_pages_from_pdf(file_path)
    return "\n\n".join(page["text"] for page in pages)


def extract_pages_from_pdf(file_path: str) -> list[dict]:
    """Return non-empty PDF pages with one-based page numbers."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    reader = PdfReader(str(path))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page_number": page_number, "text": text})
    return pages