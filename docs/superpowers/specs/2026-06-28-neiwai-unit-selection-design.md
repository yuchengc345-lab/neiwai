# neiwai Unit Selection Design

## Summary

Add a unit-selection flow to the existing single-file quiz app so users can choose one of the 7 nursing units before starting practice.

The selected unit becomes the active quiz scope. Progress, correct count, wrong count, and completion summary apply only to that selected unit.

## Goals

- Let the user choose a unit before entering quiz mode.
- Keep the existing answer-feedback behavior unchanged.
- Keep the runtime as a single deployable `index.html`.
- Preserve mobile-first simplicity.
- Allow the user to return to unit selection without refreshing the page.

## Non-Goals

- No multi-unit mixed practice mode in this change.
- No per-unit persistent history in this change.
- No question-number jump feature in this change.

## Current App State

- The current app loads directly into question view.
- All questions are already embedded in one `questions` array.
- Each question already includes a `unit` field.
- The current quiz logic assumes one global question list and one linear session.

## Recommended Approach

Use a two-screen flow inside the existing single-file app:

1. Unit selection screen
2. Quiz screen

This is preferred over a top-only dropdown because:

- it is clearer on mobile
- it matches the user's idea of "選題"
- it lowers accidental scope switching during practice
- it can be added with minimal change to the existing data model

## User Flow

1. User opens the site.
2. The site shows a unit selection screen with 7 tappable unit cards.
3. Each card shows:
   - unit name
   - question count for that unit
4. User taps a unit.
5. The app switches into quiz mode using only that unit's questions.
6. The quiz screen shows:
   - current unit name
   - progress within that unit
   - correct count within that unit
   - wrong count within that unit
   - existing option-answering behavior
7. User can tap `重選單元` to return to the unit selection screen.
8. Returning to selection resets the active quiz session state.

## UI Design

### Unit Selection Screen

- Reuse the current visual language: soft light background, rounded cards, blue accent.
- Show a compact title such as `選擇單元開始刷題`.
- Show one stacked card per unit for mobile readability.
- Each card should include:
  - unit title
  - compact question count, for example `90 題`
- Cards should feel clearly tappable, with the same subtle press feedback used elsewhere.

### Quiz Screen Changes

- Keep the current progress panel and question layout.
- Add a small top action button: `重選單元`.
- Continue to show the active unit name prominently.
- Keep the `下一題` behavior unchanged.

## Data and State Design

No source-document format changes are needed.

The runtime should derive grouped units from the existing `questions` array, for example:

```js
const units = [
  {
    name: "單元5 腫瘤疾病與護理",
    questions: [...]
  }
];
```

Recommended front-end state additions:

```js
let activeUnitName = "";
let activeQuestions = [];
let currentScreen = "units"; // "units" | "quiz"
```

Quiz state such as:

- `currentIndex`
- `correctCount`
- `wrongCount`
- `answeredCurrent`

should reset whenever:

- a new unit is selected
- the user returns to unit selection
- the user restarts the selected unit

## Behavior Rules

- On first load, show the unit selection screen instead of auto-starting the first question.
- Selecting a unit must reset all quiz counters and start at question 1 of that unit.
- `第 X / Y 題` must use the selected unit's total question count.
- Completion summary must reflect the selected unit only.
- `重選單元` returns to the selection screen and clears current quiz progress.
- If a unit unexpectedly has zero questions, show a friendly unavailable message and prevent entering quiz mode.

## Architecture Impact

This change should remain front-end only.

No changes are required to:

- Word parsing logic
- extraction scripts
- question object shape
- deployment structure

Expected touched areas:

- single-file HTML structure
- CSS for unit cards and selection screen
- JavaScript screen state and quiz-session scoping
- tests covering unit grouping and unit-switch behavior

## Error Handling

- If unit grouping fails, fall back to a simple empty-state message rather than showing broken controls.
- If a selected unit has no available questions, do not enter quiz mode.
- If `activeQuestions` is empty in quiz mode, show a safe recovery message and a return button to unit selection.

## Verification Requirements

Implementation is not complete until all of the following are true:

- site opens to unit selection screen
- all 7 units are shown
- each unit shows a question count
- tapping a unit starts that unit only
- progress uses that unit's question total
- answer feedback still works exactly as before
- `重選單元` returns to selection screen
- choosing a new unit resets progress and counters
- final summary is scoped to the selected unit
- mobile layout remains clean and touch-friendly

## Scope Check

This is a focused front-end enhancement and fits in a single implementation cycle.
