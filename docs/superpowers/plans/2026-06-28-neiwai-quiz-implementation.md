# neiwai Quiz App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a GitHub-ready, mobile-first single-file quiz app for 7 nursing question documents and deploy it on GitHub Pages.

**Architecture:** Use a development-time Python extraction pipeline to parse the 7 `.docx` files into a normalized question list, then embed that list into a single static `index.html` containing all HTML, CSS, and JavaScript. Keep runtime deployment to one file while allowing small helper scripts and tests inside the repository for regeneration and verification.

**Tech Stack:** Static HTML/CSS/JavaScript, Python 3 with `python-docx`, Git, GitHub Pages

---

## File Structure

- Create: `index.html`
  - Final deployable app with embedded styles, logic, and `questions` data.
- Create: `scripts/extract_questions.py`
  - Reads the 7 Word files and produces normalized question objects.
- Create: `scripts/build_index.py`
  - Injects normalized question data into the single-file app template.
- Create: `scripts/check_questions.py`
  - Validates that all parsed questions contain 4 options, a valid answer index, and non-empty text.
- Create: `tests/test_extract_questions.py`
  - Parser-focused tests for answer extraction, option splitting, note attachment, and malformed-input handling.
- Create: `tests/test_build_index.py`
  - Generation-focused tests for embedding question JSON into `index.html`.
- Create: `README.md`
  - Minimal local usage and GitHub Pages deployment notes.
- Create: `.gitignore`
  - Ignore Python cache and temporary outputs.

## Task 1: Initialize Repository Skeleton

**Files:**
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Write the failing test**

Create `tests/test_build_index.py` with:

```python
from pathlib import Path


def test_project_files_expected_to_exist():
    assert Path("README.md").exists()
    assert Path(".gitignore").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_project_files_expected_to_exist -v
```

Expected: `FAIL` because the files do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `.gitignore` with:

```gitignore
__pycache__/
*.pyc
.pytest_cache/
tmp/
build/
```

Create `README.md` with:

```md
# neiwai

Single-file nursing quiz app for GitHub Pages.
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_project_files_expected_to_exist -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add .gitignore README.md tests/test_build_index.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "chore: initialize quiz app repository skeleton"
```

## Task 2: Build Parser Tests First

**Files:**
- Create: `tests/test_extract_questions.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_extract_questions.py` with:

```python
from scripts.extract_questions import attach_notes, parse_question_paragraph


def test_parse_question_paragraph_extracts_answer_and_options():
    parsed = parse_question_paragraph(
        "（Ｃ）12有關範例題目何者正確？(A)選項一　(B)選項二　(C)選項三　(D)選項四。(112.2.高)",
        "單元X"
    )
    assert parsed["unit"] == "單元X"
    assert parsed["answer"] == 2
    assert parsed["question"] == "有關範例題目何者正確？"
    assert parsed["options"] == ["選項一", "選項二", "選項三", "選項四"]


def test_attach_notes_adds_explanation_to_previous_question():
    questions = [
        {
            "id": "unitx-001",
            "unit": "單元X",
            "question": "題目",
            "options": ["A", "B", "C", "D"],
            "answer": 0,
            "explanation": ""
        }
    ]
    attach_notes(questions, "註：這是解析")
    assert questions[0]["explanation"] == "這是解析"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_extract_questions.py -v
```

Expected: `FAIL` with import errors because `scripts/extract_questions.py` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/extract_questions.py` with:

```python
import re

ANSWER_MAP = {"Ａ": 0, "Ｂ": 1, "Ｃ": 2, "Ｄ": 3}


def parse_question_paragraph(text: str, unit: str) -> dict:
    answer_match = re.match(r"^（([Ａ-Ｄ])）[0-9A-Za-z]+", text)
    if not answer_match:
        raise ValueError(f"Unrecognized question format: {text}")

    answer = ANSWER_MAP[answer_match.group(1)]
    body = re.sub(r"^（[Ａ-Ｄ]）[0-9A-Za-z]+", "", text)
    parts = re.split(r"\([A-D]\)", body)
    if len(parts) < 5:
        raise ValueError(f"Missing options: {text}")

    question_text = parts[0].strip()
    options = []
    for raw in parts[1:5]:
        clean = re.split(r"。\([0-9]{2,3}\.", raw, maxsplit=1)[0].strip("　 。")
        options.append(clean)

    return {
        "id": "",
        "unit": unit,
        "question": question_text,
        "options": options,
        "answer": answer,
        "explanation": ""
    }


def attach_notes(questions: list[dict], note_text: str) -> None:
    if questions and note_text.startswith("註："):
        questions[-1]["explanation"] = note_text.replace("註：", "", 1).strip()
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_extract_questions.py -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add scripts/extract_questions.py tests/test_extract_questions.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "test: establish parser expectations for quiz question extraction"
```

## Task 3: Expand Parser to Real Document Extraction

**Files:**
- Modify: `scripts/extract_questions.py`
- Create: `scripts/check_questions.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_extract_questions.py`:

```python
from scripts.extract_questions import fallback_explanation, normalize_question_id


def test_normalize_question_id_generates_stable_ids():
    assert normalize_question_id("單元5 腫瘤疾病與護理", 1) == "unit5-001"


def test_fallback_explanation_mentions_correct_option():
    question = {
        "question": "題目",
        "options": ["甲", "乙", "丙", "丁"],
        "answer": 1,
        "explanation": ""
    }
    text = fallback_explanation(question)
    assert "乙" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_extract_questions.py::test_normalize_question_id_generates_stable_ids tests/test_extract_questions.py::test_fallback_explanation_mentions_correct_option -v
```

Expected: `FAIL` because the new functions are not implemented yet.

- [ ] **Step 3: Write minimal implementation**

Update `scripts/extract_questions.py` to include:

```python
from pathlib import Path
from docx import Document


def normalize_question_id(unit: str, index: int) -> str:
    unit_number = re.search(r"單元(\d+)", unit)
    prefix = unit_number.group(1) if unit_number else "x"
    return f"unit{prefix}-{index:03d}"


def fallback_explanation(question: dict) -> str:
    correct = question["options"][question["answer"]]
    return f"本題正確答案為「{correct}」，建議回到原題幹與選項關鍵字重新比對。"


def extract_questions_from_docx(path: str, unit: str) -> list[dict]:
    doc = Document(path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    questions = []

    for text in paragraphs:
        if text.startswith("（"):
            question = parse_question_paragraph(text, unit)
            question["id"] = normalize_question_id(unit, len(questions) + 1)
            questions.append(question)
        elif text.startswith("註："):
            attach_notes(questions, text)

    for question in questions:
        if not question["explanation"]:
            question["explanation"] = fallback_explanation(question)

    return questions


def extract_all_sources() -> list[dict]:
    sources = [
        (r"C:\Users\Cyril\OneDrive\Documents\單元5 腫瘤疾病與護理.docx", "單元5 腫瘤疾病與護理"),
        (r"C:\Users\Cyril\OneDrive\Documents\單元7 呼吸系統疾病與護理1.docx", "單元7 呼吸系統疾病與護理1"),
        (r"C:\Users\Cyril\OneDrive\Documents\單元8 呼吸系統疾病與護理2.docx", "單元8 呼吸系統疾病與護理2"),
        (r"C:\Users\Cyril\OneDrive\Documents\單元9 呼吸系統疾病與護理3.docx", "單元9 呼吸系統疾病與護理3"),
        (r"C:\Users\Cyril\OneDrive\Documents\單元10 心臟血管系統疾病與護理1.docx", "單元10 心臟血管系統疾病與護理1"),
        (r"C:\Users\Cyril\OneDrive\Documents\單元11 心臟血管系統疾病與護理2.docx", "單元11 心臟血管系統疾病與護理2"),
        (r"C:\Users\Cyril\OneDrive\Documents\單元12 心臟血管系統疾病與護理3.docx", "單元12 心臟血管系統疾病與護理3"),
    ]
    all_questions = []
    for path, unit in sources:
        all_questions.extend(extract_questions_from_docx(path, unit))
    return all_questions


if __name__ == "__main__":
    for item in extract_all_sources()[:3]:
        print(item)
```

Create `scripts/check_questions.py` with:

```python
from scripts.extract_questions import extract_all_sources


def main() -> None:
    questions = extract_all_sources()
    assert questions, "No questions extracted"
    for item in questions:
        assert item["question"].strip(), f"Empty question: {item['id']}"
        assert len(item["options"]) == 4, f"Option count error: {item['id']}"
        assert 0 <= item["answer"] <= 3, f"Answer range error: {item['id']}"
        assert item["explanation"].strip(), f"Missing explanation: {item['id']}"
    print(f"Validated {len(questions)} questions")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_extract_questions.py -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add scripts/extract_questions.py scripts/check_questions.py tests/test_extract_questions.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "feat: extract and validate nursing quiz questions from source documents"
```

## Task 4: Build HTML Generation Tests

**Files:**
- Create: `scripts/build_index.py`
- Modify: `tests/test_build_index.py`

- [ ] **Step 1: Write the failing test**

Replace `tests/test_build_index.py` with:

```python
from scripts.build_index import render_index


def test_render_index_embeds_question_json_and_title():
    html = render_index(
        [
            {
                "id": "unit5-001",
                "unit": "單元5 腫瘤疾病與護理",
                "question": "題目內容",
                "options": ["A1", "B1", "C1", "D1"],
                "answer": 1,
                "explanation": "解析內容"
            }
        ]
    )
    assert "<title>內外護理刷題</title>" in html
    assert "const questions =" in html
    assert "題目內容" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_render_index_embeds_question_json_and_title -v
```

Expected: `FAIL` because `scripts/build_index.py` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `scripts/build_index.py` with:

```python
import json


def render_index(questions: list[dict]) -> str:
    data = json.dumps(questions, ensure_ascii=False, indent=2)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>內外護理刷題</title>
</head>
<body>
  <div id="app"></div>
  <script>
    const questions = {data};
  </script>
</body>
</html>
"""
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_render_index_embeds_question_json_and_title -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add scripts/build_index.py tests/test_build_index.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "test: define html generation contract for single-file quiz app"
```

## Task 5: Implement the Single-File Quiz UI

**Files:**
- Modify: `scripts/build_index.py`
- Create: `index.html`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_build_index.py`:

```python
def test_render_index_contains_required_ui_labels():
    html = render_index(
        [
            {
                "id": "unit5-001",
                "unit": "單元5 腫瘤疾病與護理",
                "question": "題目內容",
                "options": ["A1", "B1", "C1", "D1"],
                "answer": 1,
                "explanation": "解析內容"
            }
        ]
    )
    assert "第 <span id=\"current-number\">" in html
    assert "下一題" in html
    assert "解析" in html
    assert "correct-count" in html
    assert "wrong-count" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_render_index_contains_required_ui_labels -v
```

Expected: `FAIL` because the minimal HTML shell does not include the required UI.

- [ ] **Step 3: Write minimal implementation**

Replace `render_index` in `scripts/build_index.py` with:

```python
import json


def render_index(questions: list[dict]) -> str:
    data = json.dumps(questions, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>內外護理刷題</title>
  <style>
    :root {{
      --bg: #f6f3ee;
      --surface: rgba(255,255,255,0.88);
      --line: #d7dde8;
      --text: #17324d;
      --blue: #3f78c8;
      --green: #3aa76d;
      --red: #de6b63;
      --note: #fff7df;
      --shadow: 0 12px 30px rgba(23, 50, 77, 0.08);
      --radius: 20px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Noto Sans TC", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top, rgba(92,148,223,0.22), transparent 32%),
        linear-gradient(180deg, #f7f4ef 0%, #eef4fb 100%);
      color: var(--text);
    }}
    .shell {{
      width: min(100%, 720px);
      margin: 0 auto;
      padding: 16px 16px 32px;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid rgba(255,255,255,0.65);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}
    .progress-panel {{ padding: 16px; position: sticky; top: 0; z-index: 2; }}
    .question-panel {{ margin-top: 16px; padding: 18px; }}
    .options {{ display: grid; gap: 12px; margin-top: 16px; }}
    .option {{
      width: 100%;
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 18px;
      padding: 16px;
      text-align: left;
      font-size: 16px;
      color: var(--text);
      transition: transform 0.12s ease, border-color 0.12s ease, background 0.12s ease;
    }}
    .option:active {{ transform: scale(0.98); }}
    .option.correct {{ background: #e8f8ee; border-color: var(--green); color: #145535; }}
    .option.wrong {{ background: #fdebea; border-color: var(--red); color: #8a2f2a; }}
    .option:disabled {{ opacity: 1; }}
    .explanation {{
      display: none;
      margin-top: 16px;
      padding: 16px;
      border-radius: 18px;
      background: var(--note);
      border: 1px solid #f0dca0;
      line-height: 1.7;
    }}
    .explanation.show {{ display: block; }}
    .progress-bar {{
      overflow: hidden;
      height: 10px;
      margin-top: 12px;
      border-radius: 999px;
      background: #dde7f2;
    }}
    .progress-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #5e98df, #3aa76d);
    }}
    .next-button {{
      width: 100%;
      margin-top: 18px;
      padding: 16px;
      border: none;
      border-radius: 18px;
      background: #bfd1e5;
      color: #f8fbff;
      font-size: 17px;
      font-weight: 700;
    }}
    .next-button.enabled {{ background: linear-gradient(135deg, #4f89d8, #2f6dc7); }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="panel progress-panel">
      <div id="unit-label"></div>
      <div>第 <span id="current-number">1</span> / <span id="total-number">1</span> 題</div>
      <div>答對 <span id="correct-count">0</span> · 錯題 <span id="wrong-count">0</span></div>
      <div class="progress-bar"><div id="progress-fill" class="progress-fill"></div></div>
    </section>
    <section class="panel question-panel">
      <h1 id="question-text"></h1>
      <div id="options" class="options"></div>
      <section id="explanation" class="explanation">
        <strong>解析</strong>
        <p id="explanation-text"></p>
      </section>
      <button id="next-button" class="next-button" disabled>下一題</button>
    </section>
  </main>
  <script>
    const questions = {data};
  </script>
</body>
</html>
"""
```

Create `index.html` from generated output by adding this to `scripts/build_index.py`:

```python
from pathlib import Path
from scripts.extract_questions import extract_all_sources


def main() -> None:
    html = render_index(extract_all_sources())
    Path("index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_render_index_contains_required_ui_labels -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add scripts/build_index.py tests/test_build_index.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "feat: add single-file quiz ui shell and generation entrypoint"
```

## Task 6: Implement Runtime Quiz Logic

**Files:**
- Modify: `scripts/build_index.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_build_index.py`:

```python
def test_render_index_contains_runtime_handlers():
    html = render_index(
        [
            {
                "id": "unit5-001",
                "unit": "單元5 腫瘤疾病與護理",
                "question": "題目內容",
                "options": ["A1", "B1", "C1", "D1"],
                "answer": 1,
                "explanation": "解析內容"
            }
        ]
    )
    assert "function renderQuestion()" in html
    assert "function handleAnswer(selectedIndex)" in html
    assert "nextButton.disabled = !answeredCurrent" in html
    assert "explanation.classList.add('show')" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_render_index_contains_runtime_handlers -v
```

Expected: `FAIL` because the generated HTML still lacks runtime behavior.

- [ ] **Step 3: Write minimal implementation**

Append this script body inside the generated HTML after `const questions = ...`:

```javascript
    let currentIndex = 0;
    let correctCount = 0;
    let wrongCount = 0;
    let answeredCurrent = false;

    const unitLabel = document.getElementById('unit-label');
    const currentNumber = document.getElementById('current-number');
    const totalNumber = document.getElementById('total-number');
    const correctCountNode = document.getElementById('correct-count');
    const wrongCountNode = document.getElementById('wrong-count');
    const progressFill = document.getElementById('progress-fill');
    const questionText = document.getElementById('question-text');
    const options = document.getElementById('options');
    const explanation = document.getElementById('explanation');
    const explanationText = document.getElementById('explanation-text');
    const nextButton = document.getElementById('next-button');

    function updateProgress() {
      currentNumber.textContent = String(currentIndex + 1);
      totalNumber.textContent = String(questions.length);
      correctCountNode.textContent = String(correctCount);
      wrongCountNode.textContent = String(wrongCount);
      const ratio = questions.length ? (currentIndex / questions.length) * 100 : 0;
      progressFill.style.width = `${ratio}%`;
      nextButton.disabled = !answeredCurrent;
      nextButton.classList.toggle('enabled', answeredCurrent);
    }

    function renderQuestion() {
      const item = questions[currentIndex];
      answeredCurrent = false;
      unitLabel.textContent = item.unit;
      questionText.textContent = item.question;
      explanationText.textContent = item.explanation;
      explanation.classList.remove('show');
      options.innerHTML = '';
      item.options.forEach((label, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'option';
        button.textContent = `${String.fromCharCode(65 + index)}. ${label}`;
        button.addEventListener('click', () => handleAnswer(index));
        options.appendChild(button);
      });
      updateProgress();
    }

    function handleAnswer(selectedIndex) {
      if (answeredCurrent) return;
      answeredCurrent = true;
      const item = questions[currentIndex];
      const buttons = [...options.querySelectorAll('.option')];
      buttons.forEach((button) => { button.disabled = true; });
      if (selectedIndex === item.answer) {
        correctCount += 1;
        buttons[selectedIndex].classList.add('correct');
      } else {
        wrongCount += 1;
        buttons[selectedIndex].classList.add('wrong');
        buttons[item.answer].classList.add('correct');
      }
      explanation.classList.add('show');
      updateProgress();
    }

    function showCompletion() {
      unitLabel.textContent = '本輪完成';
      questionText.textContent = `你已完成 ${questions.length} 題`;
      options.innerHTML = '';
      explanation.classList.add('show');
      explanationText.textContent = `答對 ${correctCount} 題，錯題 ${wrongCount} 題。`;
      nextButton.textContent = '重新開始';
      nextButton.disabled = false;
      nextButton.classList.add('enabled');
    }

    nextButton.addEventListener('click', () => {
      if (!answeredCurrent && currentIndex < questions.length) return;
      if (currentIndex === questions.length - 1 && answeredCurrent) {
        currentIndex = 0;
        correctCount = 0;
        wrongCount = 0;
        nextButton.textContent = '下一題';
        renderQuestion();
        return;
      }
      currentIndex += 1;
      if (currentIndex >= questions.length) {
        currentIndex = questions.length - 1;
        showCompletion();
        return;
      }
      renderQuestion();
    });

    if (questions.length) {
      renderQuestion();
    } else {
      unitLabel.textContent = '目前沒有題目';
      questionText.textContent = '請先確認題庫是否成功匯入。';
      nextButton.style.display = 'none';
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_render_index_contains_runtime_handlers -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add scripts/build_index.py tests/test_build_index.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "feat: add quiz runtime logic for answer feedback and progression"
```

## Task 7: Generate Final `index.html` and Validate Data

**Files:**
- Modify: `index.html`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_build_index.py`:

```python
from pathlib import Path


def test_generated_index_exists_and_contains_question_array():
    html = Path("index.html").read_text(encoding="utf-8")
    assert "const questions =" in html
    assert "單元5 腫瘤疾病與護理" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_generated_index_exists_and_contains_question_array -v
```

Expected: `FAIL` because `index.html` has not yet been generated.

- [ ] **Step 3: Write minimal implementation**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/check_questions.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/build_index.py
```

Update `README.md` to:

```md
# neiwai

Single-file nursing quiz app for GitHub Pages.

## Local regeneration

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/check_questions.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/build_index.py
```

## Deploy

Push the repository to GitHub and enable GitHub Pages from the main branch root.
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add index.html README.md scripts/check_questions.py scripts/build_index.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "build: generate final single-file quiz app and usage docs"
```

## Task 8: Verify Front-End Requirements Before Publish

**Files:**
- Verify: `index.html`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_build_index.py`:

```python
def test_generated_html_contains_required_interaction_strings():
    html = Path("index.html").read_text(encoding="utf-8")
    assert "下一題" in html
    assert "解析" in html
    assert "wrongCount += 1" in html
    assert "buttons[item.answer].classList.add('correct')" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_generated_html_contains_required_interaction_strings -v
```

Expected: `FAIL` if generation has drifted from required runtime behavior.

- [ ] **Step 3: Write minimal implementation**

If the test fails, update `scripts/build_index.py` so the generated runtime includes the required strings and behavior. The core implementation block should still contain:

```javascript
      if (selectedIndex === item.answer) {
        correctCount += 1;
        buttons[selectedIndex].classList.add('correct');
      } else {
        wrongCount += 1;
        buttons[selectedIndex].classList.add('wrong');
        buttons[item.answer].classList.add('correct');
      }
      explanation.classList.add('show');
```

Then regenerate:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/build_index.py
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests/test_build_index.py::test_generated_html_contains_required_interaction_strings -v
```

Expected: `PASS`

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add index.html scripts/build_index.py tests/test_build_index.py
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "test: verify generated html satisfies quiz interaction requirements"
```

## Task 9: Connect to GitHub Repository and Publish

**Files:**
- Modify: local git metadata

- [ ] **Step 1: Write the failing test**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe remote -v
```

Expected: no configured `origin` for `yuchengc345-lab/neiwai`, or command failure if git is not initialized yet.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe status --short --branch
```

Expected: failure if the directory is not a git repository yet.

- [ ] **Step 3: Write minimal implementation**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe init
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe branch -M main
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe remote add origin https://github.com/yuchengc345-lab/neiwai.git
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe add .
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe commit -m "feat: publish mobile-first nursing quiz app"
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe push -u origin main
```

If remote history already exists, use:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe fetch origin
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe pull --rebase origin main
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe remote -v
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe status --short --branch
```

Expected:

- `origin` points to `https://github.com/yuchengc345-lab/neiwai.git`
- branch is `main`
- working tree is clean or only contains intentionally uncommitted artifacts

- [ ] **Step 5: Commit**

Run:

```bash
C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe log --oneline -n 3
```

Expected: latest commit includes the publish-ready quiz app.

## Task 10: Enable GitHub Pages and Return Shareable Link

**Files:**
- Verify: GitHub repository settings state

- [ ] **Step 1: Write the failing test**

Open the repository after push and check whether GitHub Pages is already serving from the main branch root.

Expected: Pages may not be enabled yet.

- [ ] **Step 2: Run test to verify it fails**

Check the expected public URL:

```text
https://yuchengc345-lab.github.io/neiwai/
```

Expected: unavailable until Pages is enabled and deployed.

- [ ] **Step 3: Write minimal implementation**

Enable GitHub Pages for repository `yuchengc345-lab/neiwai` using:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/ (root)`

Then wait for deployment completion.

- [ ] **Step 4: Run test to verify it passes**

Verify the site loads at:

```text
https://yuchengc345-lab.github.io/neiwai/
```

Expected: the quiz app opens and shows the first question with progress UI.

- [ ] **Step 5: Commit**

No code commit required for this step. Record the final live URL in the delivery summary.

## Self-Review

### Spec coverage

- Single-file runtime app: covered by Tasks 4 through 8.
- 7 provided documents only: covered by Task 3 fixed source list.
- Mobile-first UI and required answer behavior: covered by Tasks 5, 6, and 8.
- Explanation strategy including `註：` notes and fallback explanations: covered by Task 3 and runtime display in Task 6.
- GitHub repository setup and Pages publish: covered by Tasks 9 and 10.

### Placeholder scan

- No `TODO`, `TBD`, or deferred implementation markers remain.
- Each code-changing task includes explicit file paths, code blocks, and commands.

### Type consistency

- Parsed question object keys remain `id`, `unit`, `question`, `options`, `answer`, `explanation` across parser, builder, and runtime.
- Runtime function names are consistently `renderQuestion`, `handleAnswer`, `showCompletion`, and `updateProgress`.
