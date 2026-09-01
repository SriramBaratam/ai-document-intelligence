"""Reliable document-grounded quiz generation for the AI Document Intelligence app."""

import json
import re
from typing import Any

from app.generation.rag import LlamaGenerator


def _extract_json(text: str) -> dict[str, Any]:
    """Parse a JSON object from Ollama output, including optional code fences."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Quiz model did not return a JSON object")
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Quiz model returned invalid JSON near line {exc.lineno}, column {exc.colno}"
        ) from exc


def _normalize_questions(data: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    """Keep only complete, unambiguous four-option questions."""
    raw_questions = data.get("questions")
    if not isinstance(raw_questions, list):
        return []

    questions: list[dict[str, Any]] = []
    for item in raw_questions:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        options = item.get("options")
        if not question or not isinstance(options, list) or len(options) != 4:
            continue
        try:
            answer_index = int(item.get("answer_index"))
        except (TypeError, ValueError):
            continue
        if answer_index not in range(4):
            continue

        options = [str(option).strip() for option in options]
        if any(not option for option in options) or len(set(options)) != 4:
            continue

        questions.append({
            "question": question,
            "options": options,
            "answer_index": answer_index,
            "explanation": str(item.get("explanation", "")).strip(),
            "source": str(item.get("source", "Document context")).strip(),
        })
        if len(questions) >= limit:
            break

    return questions


def generate_quiz(
    generator: LlamaGenerator,
    context: str,
    num_questions: int = 10,
    difficulty: str = "mixed",
    instruction: str = "Conduct a quiz for me",
) -> dict[str, Any]:
    """Generate a validated quiz using only retrieved document context.

    ``instruction`` is intentionally passed through to the model so natural
    language requests such as "test me on chapter 2 with hard questions" are
    actually used rather than being reduced to only the dropdown settings.
    """
    num_questions = max(3, min(int(num_questions), 20))
    difficulty = difficulty if difficulty in {"easy", "medium", "hard", "mixed"} else "mixed"
    instruction = (instruction or "Conduct a quiz for me").strip()[:1000]

    prompt = f"""
You are the quiz agent inside a document intelligence application.
The user wants to be tested on the supplied documents.

USER'S NATURAL-LANGUAGE REQUEST:
{instruction}

QUIZ SETTINGS:
- Number of questions: {num_questions}
- Difficulty: {difficulty}

Create exactly {num_questions} multiple-choice questions using ONLY the document context below.
Honor the user's request when it specifies a topic, chapter, section, concept, question style, or difficulty.
If the request is broad, cover the most important concepts across the supplied context.
Never use outside knowledge or invent facts.
Every question must be directly answerable from the context.
Each question needs exactly four distinct options and exactly one correct answer.
answer_index must be an integer from 0 to 3 and must identify the correct option.
Keep explanations short and evidence-based.
Use the source filename/page from the context when possible.
Avoid duplicate questions and avoid asking about information that is not explicitly supported.

Return ONLY valid JSON. No markdown, no commentary, no code fences.
Required shape:
{{
  "title": "Document Quiz",
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer_index": 0,
      "explanation": "...",
      "source": "filename, page"
    }}
  ]
}}

DOCUMENT CONTEXT:
{context}
"""

    raw = generator.generate(
        prompt,
        max_tokens=max(3072, num_questions * 420),
        json_mode=True,
        temperature=0.1,
    )
    data = _extract_json(raw)
    questions = _normalize_questions(data, num_questions)

    if len(questions) < 3:
        raise ValueError("The document did not contain enough reliable material to create a quiz")

    return {
        "title": str(data.get("title") or "Document Quiz"),
        "questions": questions,
        "question_count": len(questions),
        "difficulty": difficulty,
        "instruction": instruction,
    }
