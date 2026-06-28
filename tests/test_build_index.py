import unittest
from pathlib import Path

from scripts.build_index import render_index


SAMPLE_QUESTIONS = [
    {
        "id": "unit5-001",
        "unit": "單元5 腫瘤疾病與護理",
        "question": "題目內容 A",
        "options": ["A1", "B1", "C1", "D1"],
        "answer": 1,
        "explanation": "解析內容 A",
    },
    {
        "id": "unit7-001",
        "unit": "單元7 呼吸系統疾病與護理1",
        "question": "題目內容 B",
        "options": ["A2", "B2", "C2", "D2"],
        "answer": 0,
        "explanation": "解析內容 B",
    },
]


class ProjectSkeletonTests(unittest.TestCase):
    def test_project_files_expected_to_exist(self):
        self.assertTrue(Path("README.md").exists())
        self.assertTrue(Path(".gitignore").exists())

    def test_render_index_embeds_question_json_and_title(self):
        html = render_index(SAMPLE_QUESTIONS[:1])
        self.assertIn("<title>", html)
        self.assertIn("const questions =", html)
        self.assertIn("題目內容 A", html)

    def test_render_index_contains_required_ui_labels(self):
        html = render_index(SAMPLE_QUESTIONS[:1])
        self.assertIn('id="current-number"', html)
        self.assertIn("下一題", html)
        self.assertIn("解析", html)
        self.assertIn("correct-count", html)
        self.assertIn("wrong-count", html)

    def test_render_index_contains_runtime_handlers(self):
        html = render_index(SAMPLE_QUESTIONS[:1])
        self.assertIn("function renderQuestion()", html)
        self.assertIn("function handleAnswer(selectedIndex)", html)
        self.assertIn("nextButton.disabled = !answeredCurrent", html)
        self.assertIn("explanation.classList.add('show')", html)

    def test_render_index_contains_unit_selection_ui(self):
        html = render_index(SAMPLE_QUESTIONS[:1])
        self.assertIn("選擇單元開始刷題", html)
        self.assertIn('id="unit-selection"', html)
        self.assertIn("重選單元", html)

    def test_render_index_contains_unit_grouping_logic(self):
        html = render_index(SAMPLE_QUESTIONS[:1])
        self.assertIn("function buildUnits()", html)
        self.assertIn("let activeQuestions = []", html)
        self.assertIn("let currentScreen = 'units'", html)
        self.assertIn("startUnit(unitName)", html)

    def test_render_index_scopes_progress_to_active_unit(self):
        html = render_index(SAMPLE_QUESTIONS)
        self.assertIn("totalNumber.textContent = String(activeQuestions.length)", html)
        self.assertIn("const item = activeQuestions[currentIndex]", html)
        self.assertIn("const ratio = activeQuestions.length ?", html)

    def test_generated_html_contains_return_to_unit_selection_flow(self):
        html = render_index(SAMPLE_QUESTIONS[:1])
        self.assertIn("backToUnitsButton.addEventListener('click'", html)
        self.assertIn("currentScreen = 'units'", html)
        self.assertIn("renderUnitSelection()", html)
        self.assertIn("renderScreen()", html)

    def test_generated_index_exists_and_contains_question_array(self):
        html = Path("index.html").read_text(encoding="utf-8")
        self.assertIn("const questions =", html)
        self.assertIn("單元5", html)

    def test_generated_html_contains_required_interaction_strings(self):
        html = Path("index.html").read_text(encoding="utf-8")
        self.assertIn("下一題", html)
        self.assertIn("解析", html)
        self.assertIn("wrongCount += 1", html)
        self.assertIn("buttons[item.answer].classList.add('correct')", html)


if __name__ == "__main__":
    unittest.main()
