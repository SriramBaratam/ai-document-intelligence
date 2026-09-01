"""Document-grounded quiz generation with strict structured-output validation."""

import json
import re
from typing import Any

from app.generation.rag import LlamaGenerator

_ALLOWED_DIFFICULTIES = {"easy", "medium", "hard", "mixed"}


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Quiz model did not return a JSON object")
    try:
        value = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Quiz model returned invalid JSON near line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("Quiz model returned JSON, but not a quiz object")
    return value


def _normalize_questions(data: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    raw_questions = data.get("questions")
    if not isinstance(raw_questions, list):
        return []

    questions: list[dict[str, Any]] = []
    seen: set[str] = set()
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
        normalized_options = [str(option).strip() for option in options]
        if any(not option for option in normalized_options):
            continue
        if len(set(normalized_options)) != 4:
            continue

        key = re.sub(r"\s+", " ", question.lower())
        if key in seen:
            continue
        seen.add(key)
        questions.append(
            {
                "question": question,
                "options": normalized_options,
                "answer_index": answer_index,
                "explanation": str(item.get("explanation", "")).strip(),
                "source": str(item.get("source", "Document context")).strip(),
            }
        )
        if len(questions) >= limit:
            break
    return questions


def _build_prompt(context: str, instruction: str, num_questions: int, difficulty: str, offset: int = 0) -> str:
    numbering = (
        f"Generate questions {offset + 1} through {offset + num_questions}."
        if offset
        else f"Generate exactly {num_questions} questions."
    )
    return f"""You are the quiz agent inside a document intelligence application.

USER REQUEST (follow this, not just the dropdowns):
{instruction}

QUIZ SETTINGS:
- Difficulty: {difficulty}
- Questions requested in this call: {num_questions}
- {numbering}

Create multiple-choice questions from ONLY the supplied document context.
Natural-language requests such as "test me", "quiz me", "check my knowledge", "ask me questions", or "conduct a quiz" all mean the user wants an interactive quiz.
Honor topic, chapter, section, concept, style, and difficulty constraints expressed by the user.
If no topic is specified, cover important concepts from the indexed documents.
Never use outside knowledge or invent facts.
Every question must be answerable from the context and have exactly one correct answer.
Each question must have exactly four distinct options.
answer_index is zero-based (0, 1, 2, or 3) and MUST point to the correct option.
Avoid duplicate questions. Keep explanations short and evidence-based.
Use filename and page information from the context in source when available.

Return ONLY valid JSON. No markdown, commentary, or code fences.
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


def generate_quiz(
    generator: LlamaGenerator,
    context: str,
    num_questions: int = 10,
    difficulty: str = "mixed",
    instruction: str = "Conduct a quiz for me",
) -> dict[str, Any]:
    """Generate a validated quiz, retrying if the local model under-produces."""
    try:
        requested = int(num_questions)
    except (TypeError, ValueError):
        requested = 10
    requested = max(3, min(requested, 20))
    difficulty = difficulty if difficulty in _ALLOWED_DIFFICULTIES else "mixed"
    instruction = (instruction or "Conduct a quiz for me").strip()[:1000]

    # Smaller JSON batches are substantially safer for a local 3B model.
    first_count = min(requested, 8)
    raw = generator.generate(
        _build_prompt(context, instruction, first_count, difficulty),
        max_tokens=max(3072, first_count * 430),
        json_mode=True,
        temperature=0.1,
    )
    questions = _normalize_questions(_extract_json(raw), requested)

    if len(questions) < requested:
        remaining = requested - len(questions)
        retry_prompt = _build_prompt(
            context,
            instruction + "\nIMPORTANT: Create NEW questions and do not repeat any earlier question.",
            remaining,
            difficulty,
            offset=len(questions),
        )
        retry_raw = generator.generate(
            retry_prompt,
            max_tokens=max(2048, remaining * 430),
            json_mode=True,
            temperature=0.1,
        )
        extra = _normalize_questions(_extract_json(retry_raw), remaining)
        existing = {q["question"].lower().strip() for q in questions}
        questions.extend(q for q in extra if q["question"].lower().strip() not in existing)

    if len(questions) < 3:
        raise ValueError("The document did not contain enough reliable material to create a quiz.")

    questions = questions[:requested]
    return {
        "title": "Document Quiz",
        "questions": questions,
        "question_count": len(questions),
        "requested_count": requested,
        "difficulty": difficulty,
        "instruction": instruction,
    }
