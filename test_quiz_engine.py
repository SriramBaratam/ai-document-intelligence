from app.quiz_engine import _normalize_questions, generate_quiz


class FakeGenerator:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt, max_tokens=512, json_mode=False, temperature=0.2):
        self.prompts.append(prompt)
        return '''{"title":"Document Quiz","questions":[
          {"question":"What is the main topic?","options":["A","B","C","D"],"answer_index":1,"explanation":"The context states B.","source":"test.pdf, page 1"},
          {"question":"Which method is described?","options":["M1","M2","M3","M4"],"answer_index":2,"explanation":"The context states M3.","source":"test.pdf, page 2"},
          {"question":"What result was reported?","options":["R1","R2","R3","R4"],"answer_index":0,"explanation":"The context states R1.","source":"test.pdf, page 3"}
        ]}'''


def test_normalize_rejects_invalid_questions():
    data = {"questions": [
        {"question": "bad", "options": ["A", "B"], "answer_index": 0},
        {"question": "good", "options": ["A", "B", "C", "D"], "answer_index": 3},
    ]}
    result = _normalize_questions(data, 10)
    assert len(result) == 1
    assert result[0]["answer_index"] == 3


def test_generate_quiz_preserves_natural_language_instruction():
    generator = FakeGenerator()
    result = generate_quiz(
        generator,
        "Chapter 2 explains retrieval and embeddings.",
        num_questions=3,
        difficulty="hard",
        instruction="Test me only on chapter 2 and make it difficult",
    )
    assert result["question_count"] == 3
    assert result["difficulty"] == "hard"
    assert result["instruction"] == "Test me only on chapter 2 and make it difficult"
    assert "chapter 2" in generator.prompts[0].lower()
    assert "difficult" in generator.prompts[0].lower()
