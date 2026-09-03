from app.contradictions import _extract_json, _normalize_findings


def test_extract_json_handles_markdown_fence():
    result = _extract_json('```json\n{"contradictions": []}\n```')
    assert result == {"contradictions": []}


def test_normalize_findings_restores_source_metadata():
    pairs = [
        (
            {"document": "Deadline is March 2027.", "source": "plan-a.pdf", "page_number": 2},
            {"document": "Deadline is June 2027.", "source": "plan-b.pdf", "page_number": 5},
        )
    ]
    data = {
        "contradictions": [
            {
                "pair_index": 1,
                "is_contradiction": True,
                "title": "Conflicting deadline",
                "claim_a": "Deadline is March 2027.",
                "claim_b": "Deadline is June 2027.",
                "explanation": "The same project is assigned two different deadlines.",
                "confidence": "high",
            }
        ]
    }

    findings = _normalize_findings(data, pairs)
    assert len(findings) == 1
    assert findings[0]["document_a"] == "plan-a.pdf"
    assert findings[0]["page_a"] == 2
    assert findings[0]["document_b"] == "plan-b.pdf"
    assert findings[0]["page_b"] == 5
    assert findings[0]["confidence"] == "High"


def test_non_contradiction_is_filtered():
    pairs = [
        (
            {"document": "Revenue was $1M in 2024.", "source": "a.pdf", "page_number": 1},
            {"document": "Revenue was $1.5M in 2025.", "source": "b.pdf", "page_number": 1},
        )
    ]
    data = {"contradictions": [{"pair_index": 1, "is_contradiction": False}]}
    assert _normalize_findings(data, pairs) == []
