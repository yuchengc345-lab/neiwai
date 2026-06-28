import unittest
from pathlib import Path

from scripts.build_index import render_index


class ProjectSkeletonTests(unittest.TestCase):
    def test_project_files_expected_to_exist(self):
        self.assertTrue(Path("README.md").exists())
        self.assertTrue(Path(".gitignore").exists())

    def test_render_index_embeds_question_json_and_title(self):
        html = render_index(
            [
                {
                    "id": "unit5-001",
                    "unit": "單元5 腫瘤疾病與護理",
                    "question": "題目內容",
                    "options": ["A1", "B1", "C1", "D1"],
                    "answer": 1,
                    "explanation": "解析內容",
                }
            ]
        )
        self.assertIn("<title>內外護理刷題</title>", html)
        self.assertIn("const questions =", html)
        self.assertIn("題目內容", html)

    def test_render_index_contains_required_ui_labels(self):
        html = render_index(
            [
                {
                    "id": "unit5-001",
                    "unit": "單元5 腫瘤疾病與護理",
                    "question": "題目內容",
                    "options": ["A1", "B1", "C1", "D1"],
                    "answer": 1,
                    "explanation": "解析內容",
                }
            ]
        )
        self.assertIn('第 <span id="current-number">', html)
        self.assertIn("下一題", html)
        self.assertIn("解析", html)
        self.assertIn("correct-count", html)
        self.assertIn("wrong-count", html)

    def test_render_index_contains_runtime_handlers(self):
        html = render_index(
            [
                {
                    "id": "unit5-001",
                    "unit": "單元5 腫瘤疾病與護理",
                    "question": "題目內容",
                    "options": ["A1", "B1", "C1", "D1"],
                    "answer": 1,
                    "explanation": "解析內容",
                }
            ]
        )
        self.assertIn("function renderQuestion()", html)
        self.assertIn("function handleAnswer(selectedIndex)", html)
        self.assertIn("nextButton.disabled = !answeredCurrent", html)
        self.assertIn("explanation.classList.add('show')", html)

    def test_generated_index_exists_and_contains_question_array(self):
        html = Path("index.html").read_text(encoding="utf-8")
        self.assertIn("const questions =", html)
        self.assertIn("單元5 腫瘤疾病與護理", html)

    def test_generated_html_contains_required_interaction_strings(self):
        html = Path("index.html").read_text(encoding="utf-8")
        self.assertIn("下一題", html)
        self.assertIn("解析", html)
        self.assertIn("wrongCount += 1", html)
        self.assertIn("buttons[item.answer].classList.add('correct')", html)


if __name__ == "__main__":
    unittest.main()
