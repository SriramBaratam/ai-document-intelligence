"""Grounded quiz generation helpers for the document intelligence app."""

import json
import re
from typing import Any

from app.generation.rag import LlamaGenerator


def _extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from an LLM response, tolerating fenced code blocks."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Quiz model did not return a JSON object")
    return json.loads(cleaned[start : end + 1])


def generate_quiz(generator: LlamaGenerator, context: str, num_questions: int = 10, difficulty: str = "mixed") -> dict[str, Any]:
    """Generate multiple-choice questions grounded only in retrieved document context."""
    num_questions = max(3, min(int(num_questions), 20))
    allowed = {"easy", "medium", "hard", "mixed"}
    difficulty = difficulty if difficulty in allowed else "mixed"

    prompt = f"""
You are the quiz engine for a document intelligence application.
Create exactly {num_questions} multiple-choice questions using ONLY the supplied document context.
Difficulty: {difficulty}.
Do not use outside knowledge. Do not invent facts.
Every question must be answerable from the context.
Return ONLY valid JSON in this exact shape:
{{
  "title": "Document Quiz",
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer_index": 0,
      "explanation": "Brief explanation grounded in the context.",
      "source": "Source filename/page if available"
    }}
  ]
}}

DOCUMENT CONTEXT:
{context}
"""

    raw = generator.generate(prompt)
    data = _extract_json(raw)
    questions = data.get("questions")
    if not isinstance(questions, list):
        raise ValueError("Quiz response is missing questions")

    normalized = []
    for item in questions:
        if not isinstance(item, dict):
            continue
        options = item.get("options")
        answer_index = item.get("answer_index")
        question = str(item.get("question", "")).strip()
        if not question or not isinstance(options, list) or len(options) != 4:
            continue
        try:
            answer_index = int(answer_index)
        except (TypeError, ValueError):
            continue
        if answer_index not in range(4):
            continue
        normalized.append({
            "question": question,
            "options": [str(x) for x in options],
            "answer_index": answer_index,
            "explanation": str(item.get("explanation", "")).strip(),
            "source": str(item.get("source", "Document context")).strip(),
        })

    if len(normalized) < 3:
        raise ValueError("The document did not contain enough reliable material to create a quiz")

    return {
        "title": str(data.get("title") or "Document Quiz"),
        "questions": normalized[:num_questions],
        "question_count": len(normalized[:num_questions]),
        "difficulty": difficulty,
    }
