"""Grounded contradiction detection for indexed document collections."""

import json
import re
from typing import Any

from app.generation.rag import LlamaGenerator


def _extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from model output, including fenced responses."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Contradiction model did not return a JSON object")
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Contradiction model returned invalid JSON near line {exc.lineno}, column {exc.colno}"
        ) from exc


def _clean_confidence(value: Any) -> str:
    value = str(value or "").strip().lower()
    return {"high": "High", "medium": "Medium", "low": "Low"}.get(value, "Medium")


def _normalize_findings(data: dict[str, Any], pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> list[dict[str, Any]]:
    """Validate model findings and restore authoritative source metadata."""
    raw = data.get("contradictions")
    if not isinstance(raw, list):
        return []

    normalized: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict) or not item.get("is_contradiction"):
            continue
        try:
            pair_index = int(item.get("pair_index")) - 1
        except (TypeError, ValueError):
            continue
        if pair_index < 0 or pair_index >= len(pairs):
            continue

        left, right = pairs[pair_index]
        explanation = str(item.get("explanation", "")).strip()
        if not explanation:
            continue

        normalized.append(
            {
                "title": str(item.get("title") or "Potential contradiction").strip(),
                "document_a": left.get("source", "Unknown"),
                "page_a": left.get("page_number"),
                "claim_a": str(item.get("claim_a") or left.get("document", "")).strip(),
                "document_b": right.get("source", "Unknown"),
                "page_b": right.get("page_number"),
                "claim_b": str(item.get("claim_b") or right.get("document", "")).strip(),
                "explanation": explanation,
                "confidence": _clean_confidence(item.get("confidence")),
                "similarity": round(float(item.get("similarity", 0)), 3),
            }
        )

    return normalized


def _candidate_pairs(pipeline, max_pairs: int = 28) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Use the existing FAISS index to find semantically related chunk pairs."""
    docs = pipeline.vector_store.documents
    if len(docs) < 2:
        return []

    texts = [item.get("document", "") for item in docs]
    embeddings = pipeline.embedder.encode(texts)
    pairs: dict[tuple[int, int], tuple[dict[str, Any], dict[str, Any]]] = {}

    for i, embedding in enumerate(embeddings):
        for match in pipeline.vector_store.search(embedding, top_k=min(8, len(docs))):
            # Search returns rank rather than the original index, so recover a
            # stable document index by matching source/text metadata.
            for j, candidate in enumerate(docs):
                if j == i:
                    continue
                if candidate.get("document") != match.get("document"):
                    continue
                if candidate.get("metadata", {}) != {
                    key: match.get(key)
                    for key in candidate.get("metadata", {})
                }:
                    continue
                if match.get("score", 0) < 0.30:
                    continue
                if i == j:
                    continue
                key = tuple(sorted((i, j)))
                pairs[key] = (docs[key[0]], docs[key[1]])
                break
            if len(pairs) >= max_pairs:
                break
        if len(pairs) >= max_pairs:
            break

    return list(pairs.values())


def detect_contradictions(pipeline, max_pairs: int = 28) -> dict[str, Any]:
    """Find conservative, evidence-backed contradictions in indexed chunks."""
    if not pipeline.documents_ingested or pipeline.vector_store.index.ntotal < 2:
        return {
            "message": "At least two indexed document chunks are required for contradiction analysis.",
            "contradictions": [],
            "pairs_analyzed": 0,
        }

    pairs = _candidate_pairs(pipeline, max_pairs=max_pairs)
    if not pairs:
        return {
            "message": "No sufficiently related evidence pairs were found to compare.",
            "contradictions": [],
            "pairs_analyzed": 0,
        }

    pair_context = []
    for index, (left, right) in enumerate(pairs, start=1):
        lm = left.get("metadata", {})
        rm = right.get("metadata", {})
        pair_context.append(
            f"PAIR {index}\n"
            f"A: {lm.get('source', 'Unknown')} | page {lm.get('page_number') or 'N/A'}\n"
            f"{left.get('document', '')}\n"
            f"B: {rm.get('source', 'Unknown')} | page {rm.get('page_number') or 'N/A'}\n"
            f"{right.get('document', '')}"
        )

    prompt = f"""You are a conservative contradiction-analysis agent for a document intelligence system.
Compare ONLY the evidence pairs below.

A contradiction means two passages make incompatible factual claims about the same entity, event, metric, date, requirement, status, or definition.
Do NOT call something a contradiction when the difference is explained by:
- different dates or versions
- different populations, scopes, conditions, or entities
- different levels of precision
- one passage being broader or narrower
- a claim merely adding information
- uncertainty or lack of evidence

Never use outside knowledge. Never invent missing facts. Prefer false negatives over false positives.
Return only genuine contradictions with enough evidence to explain why the claims cannot both be true under the same context.

Return ONLY valid JSON in this exact shape:
{{
  "contradictions": [
    {{
      "pair_index": 1,
      "is_contradiction": true,
      "title": "Short useful title",
      "claim_a": "Short exact or faithful claim from A",
      "claim_b": "Short exact or faithful claim from B",
      "explanation": "Why these claims conflict under the same context",
      "confidence": "High|Medium|Low"
    }}
  ]
}}
If none are genuine contradictions, return {{"contradictions": []}}.

EVIDENCE PAIRS:
{chr(10).join(pair_context)}
"""

    raw = pipeline.generator.generate(
        prompt,
        max_tokens=2600,
        json_mode=True,
        temperature=0.05,
    )
    data = _extract_json(raw)
    findings = _normalize_findings(data, pairs)

    return {
        "message": "Contradiction analysis completed.",
        "contradictions": findings,
        "pairs_analyzed": len(pairs),
    }
