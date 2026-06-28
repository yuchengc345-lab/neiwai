# neiwai Unit Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a mobile-friendly unit selection screen so users choose one of the 7 units before starting quiz practice.

**Architecture:** Keep the single-file deployment model and the existing `questions` array. Add a front-end grouping layer that derives unit cards from embedded questions, then switch between a `units` screen and a `quiz` screen while scoping progress and scoring to the currently selected unit.

**Tech Stack:** Static HTML, embedded CSS, embedded JavaScript, Python `unittest`

---

## File Structure

- Modify: `index.html`
  - Add unit selection layout, unit-scoped state, and return-to-selection flow.
- Modify: `scripts/build_index.py`
  - Generate the updated single-file HTML with unit grouping and screen switching.
- Modify: `tests/test_build_index.py`
  - Cover unit-selection screen, unit scoping, and return flow.
- Modify: `README.md`
  - Mention that the app now starts from unit selection.

## Task 1: Add Unit Selection Test Coverage

**Files:**
- Modify: `tests/test_build_index.py`

- [ ] **Step 1: Write the failing test**

Add:

```python
    def test_render_index_contains_unit_selection_ui(self):
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
        self.assertIn("選擇單元開始刷題", html)
        self.assertIn("unit-selection", html)
        self.assertIn("重選單元", html)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index.ProjectSkeletonTests.test_render_index_contains_unit_selection_ui
```

Expected: `FAIL` because the current generated HTML does not include the new unit-selection UI.

- [ ] **Step 3: Write minimal implementation**

Update `scripts/build_index.py` so the generated HTML includes:

```html
<section id="unit-selection" class="panel unit-selection">
  <h1 class="selection-title">選擇單元開始刷題</h1>
  <div id="unit-list" class="unit-list"></div>
</section>
<button id="back-to-units" class="back-button" type="button">重選單元</button>
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index.ProjectSkeletonTests.test_render_index_contains_unit_selection_ui
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' add tests/test_build_index.py scripts/build_index.py
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' commit -m "test: define unit selection ui contract"
```

## Task 2: Add Unit Grouping and Screen State

**Files:**
- Modify: `tests/test_build_index.py`
- Modify: `scripts/build_index.py`

- [ ] **Step 1: Write the failing test**

Add:

```python
    def test_render_index_contains_unit_grouping_logic(self):
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
        self.assertIn("function buildUnits()", html)
        self.assertIn("let activeQuestions = []", html)
        self.assertIn("let currentScreen = 'units'", html)
        self.assertIn("startUnit(unitName)", html)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index.ProjectSkeletonTests.test_render_index_contains_unit_grouping_logic
```

Expected: `FAIL` because the current runtime still assumes one global active question list.

- [ ] **Step 3: Write minimal implementation**

Update generated script to include:

```javascript
let activeUnitName = "";
let activeQuestions = [];
let currentScreen = "units";

function buildUnits() {
  const unitMap = new Map();
  questions.forEach((item) => {
    if (!unitMap.has(item.unit)) unitMap.set(item.unit, []);
    unitMap.get(item.unit).push(item);
  });
  return [...unitMap.entries()].map(([name, items]) => ({ name, questions: items }));
}

function startUnit(unitName) {
  const match = units.find((unit) => unit.name === unitName);
  activeUnitName = match.name;
  activeQuestions = match.questions;
  currentIndex = 0;
  correctCount = 0;
  wrongCount = 0;
  answeredCurrent = false;
  currentScreen = "quiz";
  renderScreen();
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index.ProjectSkeletonTests.test_render_index_contains_unit_grouping_logic
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' add tests/test_build_index.py scripts/build_index.py
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' commit -m "feat: group questions by unit and add unit session state"
```

## Task 3: Scope Quiz Progress to the Selected Unit

**Files:**
- Modify: `tests/test_build_index.py`
- Modify: `scripts/build_index.py`

- [ ] **Step 1: Write the failing test**

Add:

```python
    def test_render_index_scopes_progress_to_active_unit(self):
        html = render_index(
            [
                {
                    "id": "unit5-001",
                    "unit": "單元5 腫瘤疾病與護理",
                    "question": "題目A",
                    "options": ["A1", "B1", "C1", "D1"],
                    "answer": 1,
                    "explanation": "解析A",
                },
                {
                    "id": "unit7-001",
                    "unit": "單元7 呼吸系統疾病與護理1",
                    "question": "題目B",
                    "options": ["A2", "B2", "C2", "D2"],
                    "answer": 0,
                    "explanation": "解析B",
                },
            ]
        )
        self.assertIn("totalNumber.textContent = String(activeQuestions.length)", html)
        self.assertIn("const item = activeQuestions[currentIndex]", html)
        self.assertIn("const ratio = activeQuestions.length ?", html)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index.ProjectSkeletonTests.test_render_index_scopes_progress_to_active_unit
```

Expected: `FAIL` because progress currently uses the full `questions` array.

- [ ] **Step 3: Write minimal implementation**

Update runtime so:

```javascript
totalNumber.textContent = String(activeQuestions.length);
const item = activeQuestions[currentIndex];
const ratio = activeQuestions.length ? (currentIndex / activeQuestions.length) * 100 : 0;
```

Also update completion text to use `activeQuestions.length`.

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index.ProjectSkeletonTests.test_render_index_scopes_progress_to_active_unit
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' add tests/test_build_index.py scripts/build_index.py
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' commit -m "feat: scope quiz progress and summary to active unit"
```

## Task 4: Add Return-to-Selection Flow and Regenerate `index.html`

**Files:**
- Modify: `tests/test_build_index.py`
- Modify: `scripts/build_index.py`
- Modify: `index.html`
- Modify: `README.md`

- [ ] **Step 1: Write the failing test**

Add:

```python
    def test_generated_html_contains_return_to_unit_selection_flow(self):
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
        self.assertIn("backToUnitsButton.addEventListener('click'", html)
        self.assertIn("currentScreen = 'units'", html)
        self.assertIn("renderUnitSelection()", html)
        self.assertIn("renderScreen()", html)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index.ProjectSkeletonTests.test_generated_html_contains_return_to_unit_selection_flow
```

Expected: `FAIL` because the current generated HTML still lacks the return flow.

- [ ] **Step 3: Write minimal implementation**

Update the generated runtime to include:

```javascript
function renderUnitSelection() {
  currentScreen = "units";
  unitSelection.hidden = false;
  quizScreen.hidden = true;
  backToUnitsButton.hidden = true;
}

function renderScreen() {
  if (currentScreen === "units") {
    renderUnitSelection();
    return;
  }
  unitSelection.hidden = true;
  quizScreen.hidden = false;
  backToUnitsButton.hidden = false;
  renderQuestion();
}

backToUnitsButton.addEventListener('click', () => {
  activeUnitName = "";
  activeQuestions = [];
  currentIndex = 0;
  correctCount = 0;
  wrongCount = 0;
  answeredCurrent = false;
  currentScreen = "units";
  renderScreen();
});
```

Regenerate:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m scripts.build_index
```

Update `README.md` with one line stating the app now starts from unit selection.

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_build_index tests.test_extract_questions
```

Expected: all tests `PASS`

- [ ] **Step 5: Commit**

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' add tests/test_build_index.py scripts/build_index.py index.html README.md
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe' commit -m "feat: add unit selection flow to quiz app"
```

## Self-Review

### Spec coverage

- Unit cards before quiz start: covered by Tasks 1 and 2.
- Selected unit only: covered by Task 3.
- Return to unit selection: covered by Task 4.
- Preserve existing answer feedback: maintained by Tasks 3 and 4 through scoped reuse of existing quiz logic.
- Single-file deployment unchanged: preserved by Task 4 regeneration.

### Placeholder scan

- No `TODO`, `TBD`, or undefined follow-up steps remain.
- Every code change is paired with a concrete verification command.

### Type consistency

- Runtime state consistently uses `activeUnitName`, `activeQuestions`, and `currentScreen`.
- Existing quiz state names remain unchanged: `currentIndex`, `correctCount`, `wrongCount`, `answeredCurrent`.
