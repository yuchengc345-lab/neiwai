# neiwai Explanations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate standardized explanation text for all 470 nursing quiz questions, render those explanations cleanly in the single-file quiz app, and publish the updated site to the user's GitHub repository.

**Architecture:** Keep the existing extraction pipeline and question object shape, but replace the generic fallback explanation builder in `scripts/extract_questions.py` with a standardized formatter that outputs four labeled lines. Update `scripts/build_index.py` so the explanation card preserves multi-line formatting in the browser without changing the answer flow or unit-selection behavior. Verify extraction, rebuild `index.html`, run the test suite, then commit and push the updated site.

**Tech Stack:** Python 3, `python-docx`, standard-library `re` and `json`, single-file HTML/CSS/JavaScript, GitHub repository push via Git.

---

## File Structure

- Modify: `C:\Users\Cyril\OneDrive\Documents\内外題目\scripts\extract_questions.py`
  - Add helper functions for normalizing source notes and generating the four-part explanation string.
  - Replace the current generic fallback explanation builder.
- Modify: `C:\Users\Cyril\OneDrive\Documents\内外題目\tests\test_extract_questions.py`
  - Add tests that lock the explanation format and protect source-note handling.
- Modify: `C:\Users\Cyril\OneDrive\Documents\内外題目\scripts\build_index.py`
  - Update explanation rendering so stored line breaks appear correctly in the app.
- Modify: `C:\Users\Cyril\OneDrive\Documents\内外題目\tests\test_build_index.py`
  - Add assertions for explanation rendering and multi-line display support.
- Modify: `C:\Users\Cyril\OneDrive\Documents\内外題目\index.html`
  - Regenerated artifact from `scripts/build_index.py`; do not hand-edit.

### Task 1: Lock the explanation content contract with tests

**Files:**
- Modify: `scripts/extract_questions.py:46-84`
- Modify: `tests/test_extract_questions.py:47-65`

- [ ] **Step 1: Write the failing tests for the standardized explanation format**

```python
    def test_fallback_explanation_uses_four_line_format(self):
        question = {
            "question": "有關化學治療副作用的敘述，下列何者正確？",
            "options": ["選項甲", "選項乙", "選項丙", "選項丁"],
            "answer": 1,
            "explanation": "",
        }
        text = fallback_explanation(question)
        self.assertIn("答案：選項乙", text)
        self.assertIn("作答關鍵：", text)
        self.assertIn("解析：", text)
        self.assertIn("複習提醒：", text)
        self.assertEqual(len(text.splitlines()), 4)

    def test_attach_notes_preserves_source_note_content_in_standard_format(self):
        questions = [
            {
                "id": "unitx-001",
                "unit": "單元X",
                "question": "題目",
                "options": ["A", "B", "C", "D"],
                "answer": 0,
                "explanation": "",
            }
        ]
        attach_notes(questions, "註：化學治療後應注意感染徵象與血球變化。")
        self.assertIn("答案：A", questions[0]["explanation"])
        self.assertIn("作答關鍵：", questions[0]["explanation"])
        self.assertIn("解析：化學治療後應注意感染徵象與血球變化。", questions[0]["explanation"])
        self.assertIn("複習提醒：", questions[0]["explanation"])
```

- [ ] **Step 2: Run the targeted extraction tests to verify they fail first**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_extract_questions -v
```

Expected: FAIL because `fallback_explanation()` still returns the old one-line generic text and `attach_notes()` still stores the raw note text without the four-part labels.

- [ ] **Step 3: Extend the extraction tests with full-dataset coverage expectations**

```python
    def test_extract_questions_from_docx_outputs_standardized_explanations(self):
        questions = extract_questions_from_docx(
            r"C:\Users\Cyril\OneDrive\Documents\單元5 腫瘤疾病與護理.docx",
            "單元5 腫瘤疾病與護理",
        )
        sample = questions[0]["explanation"]
        self.assertIn("答案：", sample)
        self.assertIn("作答關鍵：", sample)
        self.assertIn("解析：", sample)
        self.assertIn("複習提醒：", sample)
```

- [ ] **Step 4: Run the extraction tests again after adding the new dataset expectation**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_extract_questions::ExtractQuestionTests -v
```

Expected: FAIL until the extraction implementation is updated to emit the standardized explanation strings for both raw notes and generated fallback text.

- [ ] **Step 5: Commit the test-only red state**

```bash
git add tests/test_extract_questions.py
git commit -m "test: lock explanation generation format"
```

### Task 2: Implement standardized explanation generation in the extraction pipeline

**Files:**
- Modify: `scripts/extract_questions.py:35-84`
- Modify: `tests/test_extract_questions.py:1-69`

- [ ] **Step 1: Add small helpers that normalize text and build the four labeled lines**

```python
def normalize_sentence(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip(" 　。")
    return cleaned or "請回到題幹與答案關鍵字重新比對。"


def build_explanation(answer_text: str, clue_text: str, detail_text: str, reminder_text: str) -> str:
    return "\n".join(
        [
            f"答案：{normalize_sentence(answer_text)}",
            f"作答關鍵：{normalize_sentence(clue_text)}",
            f"解析：{normalize_sentence(detail_text)}",
            f"複習提醒：{normalize_sentence(reminder_text)}",
        ]
    )
```

- [ ] **Step 2: Update `attach_notes()` so source notes are reformatted instead of copied raw**

```python
def attach_notes(questions: list[dict], note_text: str) -> None:
    if not questions or not note_text.startswith("註："):
        return

    question = questions[-1]
    correct = question["options"][question["answer"]]
    note_body = note_text.replace("註：", "", 1).strip()
    question["explanation"] = build_explanation(
        answer_text=correct,
        clue_text=f"先抓題幹要你判斷的護理重點，再回到正確選項「{correct}」比對。",
        detail_text=note_body,
        reminder_text=f"遇到同類題時，先確認能支持正確選項「{correct}」的核心概念。",
    )
```

- [ ] **Step 3: Replace the current fallback builder with a standardized generated explanation**

```python
def fallback_explanation(question: dict) -> str:
    correct = question["options"][question["answer"]]
    return build_explanation(
        answer_text=correct,
        clue_text=f"先辨認題幹的關鍵概念，再回到選項中找出最能直接對應的「{correct}」。",
        detail_text=f"本題正確答案是「{correct}」，因為它最符合題幹在考的重點；作答時要把題幹關鍵字與正確選項內容一一對上。",
        reminder_text=f"若再次遇到類似題型，先圈出題幹重點，再優先檢查與「{correct}」相關的概念。",
    )
```

- [ ] **Step 4: Run the extraction test file until it passes**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_extract_questions -v
```

Expected: PASS, including the new assertions that require `答案： / 作答關鍵： / 解析： / 複習提醒：` labels.

- [ ] **Step 5: Validate the full extracted dataset instead of trusting the unit tests alone**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from scripts.extract_questions import extract_all_sources; q=extract_all_sources(); print(len(q)); print(sum('答案：' in item['explanation'] and '作答關鍵：' in item['explanation'] and '解析：' in item['explanation'] and '複習提醒：' in item['explanation'] for item in q))"
```

Expected:

```text
470
470
```

- [ ] **Step 6: Commit the extraction implementation**

```bash
git add scripts/extract_questions.py tests/test_extract_questions.py
git commit -m "feat: generate standardized quiz explanations"
```

### Task 3: Lock front-end explanation rendering behavior with tests

**Files:**
- Modify: `scripts/build_index.py:195-305`
- Modify: `tests/test_build_index.py:38-89`

- [ ] **Step 1: Add failing tests that require multi-line explanation rendering support**

```python
    def test_render_index_preserves_multiline_explanations(self):
        html = render_index(
            [
                {
                    "id": "unit5-001",
                    "unit": "單元5 腫瘤疾病與護理",
                    "question": "題目內容 A",
                    "options": ["A1", "B1", "C1", "D1"],
                    "answer": 1,
                    "explanation": "答案：B1\\n作答關鍵：抓關鍵字\\n解析：比對題幹\\n複習提醒：先圈重點",
                }
            ]
        )
        self.assertIn("white-space: pre-line", html)
        self.assertIn("explanationText.textContent = item.explanation", html)

    def test_generated_html_contains_standardized_explanation_labels(self):
        html = render_index(SAMPLE_QUESTIONS[:1])
        self.assertIn("答案：", html)
        self.assertIn("作答關鍵：", html)
        self.assertIn("複習提醒：", html)
```

- [ ] **Step 2: Run the build-index tests to confirm the rendering expectations fail first**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index -v
```

Expected: FAIL because the current explanation CSS does not preserve line breaks and the sample questions do not yet use the standardized explanation labels.

- [ ] **Step 3: Update the sample test fixture so it mirrors the real explanation format**

```python
        "explanation": "答案：B1\n作答關鍵：先看題幹\n解析：這是解析內容 A\n複習提醒：回到關鍵字",
```

- [ ] **Step 4: Re-run the build-index tests after the fixture change**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index -v
```

Expected: Still FAIL until the front-end template adds the CSS needed to display the multi-line explanation string correctly.

- [ ] **Step 5: Commit the test-only red state for the front-end**

```bash
git add tests/test_build_index.py
git commit -m "test: require multiline explanation rendering"
```

### Task 4: Implement front-end rendering, rebuild the site, verify, and publish

**Files:**
- Modify: `scripts/build_index.py:195-477`
- Modify: `tests/test_build_index.py:7-93`
- Modify: `index.html` (regenerated artifact)

- [ ] **Step 1: Update the explanation block styling so stored line breaks render on the page**

```python
    .explanation-text {{
      margin: 8px 0 0;
      white-space: pre-line;
    }}
```

- [ ] **Step 2: Keep the JavaScript binding simple and rely on `textContent` plus CSS for safety**

```python
      explanationText.textContent = item.explanation;
```

- [ ] **Step 3: Rebuild the generated single-file site from the scripts**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/build_index.py
```

Expected: `C:\Users\Cyril\OneDrive\Documents\内外題目\index.html` is rewritten with the new explanation strings embedded in `const questions = ...`.

- [ ] **Step 4: Run the focused build-index tests until they pass**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index -v
```

Expected: PASS, including checks for `white-space: pre-line` and the standardized explanation labels in rendered HTML.

- [ ] **Step 5: Run full verification that covers extraction, rendering, and dataset integrity**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_extract_questions tests.test_build_index
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/check_questions.py
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from pathlib import Path; html = Path('index.html').read_text(encoding='utf-8'); print('white-space: pre-line' in html); print('答案：' in html and '作答關鍵：' in html and '解析：' in html and '複習提醒：' in html)"
```

Expected:

```text
OK
Validated 470 questions
True
True
```

- [ ] **Step 6: Commit and push the completed site update**

```bash
git add scripts/extract_questions.py scripts/build_index.py tests/test_extract_questions.py tests/test_build_index.py index.html
git commit -m "feat: add standardized explanations for all quiz questions"
$env:GIT_EXEC_PATH='C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\mingw64\bin'; & 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' push -u origin main
```

## Self-Review

- **Spec coverage:** The plan covers explanation generation, preservation of source-note meaning, front-end multi-line rendering, rebuilding `index.html`, full verification, and GitHub publication.
- **Placeholder scan:** No `TODO`, `TBD`, or “implement later” placeholders remain; every task includes exact files, commands, and example code.
- **Type consistency:** The plan keeps the existing `question` dictionary shape and uses the same `explanation` string field in extraction, rendering, tests, and generated HTML.
