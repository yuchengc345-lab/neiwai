# neiwai Explanations Design

## Summary

Generate complete explanation text for all quiz questions in the nursing quiz app, then surface those explanations when the learner answers a question.

The explanation format should be standardized so all 470 questions feel consistent, readable on mobile, and easy to improve later.

## Goals

- Ensure every quiz question has a non-empty explanation.
- Replace the current generic fallback explanation for questions that do not already have source notes.
- Keep the app as a single deployable `index.html`.
- Preserve the existing answer-feedback flow and only improve the explanation content.
- Make the explanation block easier to scan on a phone.
- Publish the updated site to the user's GitHub repository.

## Non-Goals

- No change to the question wording or answer keys.
- No persistent wrong-question history in this change.
- No per-option collapsible teaching notes in this change.
- No backend, database, or API integration.

## Current App State

- The app already shows an explanation card after the user answers.
- The app already stores an `explanation` field on each question object.
- Only a small number of questions currently have source-document notes.
- Most questions currently fall back to a short generic explanation that mainly repeats the correct answer.
- The site already supports unit selection and unit-scoped practice.

## Recommended Approach

Use a standardized four-part explanation template for every question:

1. `答案：` the correct option text
2. `作答關鍵：` the core concept or clue that should drive the choice
3. `解析：` why the correct option fits the question best
4. `複習提醒：` a short memory aid or review cue

This is preferred over long free-form paragraphs because:

- it is easier to read on mobile
- it creates consistent quality across all 470 questions
- it fits the current UI with minimal structural change
- it allows future upgrading of selected questions without redesigning the app

## Content Generation Rules

### Questions with existing source notes

- Preserve the original source note as the main explanation content source.
- Reformat it into the standardized four-part explanation block when possible.
- If the source note is too short to fill all sections cleanly, keep the original note inside `解析：` and synthesize the other sections conservatively from the question and answer.

### Questions without source notes

- Generate a new explanation from:
  - question text
  - correct option text
  - contrast against the distractors when helpful
- The generated explanation must not invent clinical facts unrelated to the question.
- Prefer concise educational language over textbook-length exposition.
- Keep each generated explanation readable in one mobile screen without excessive scrolling when possible.

### Tone and format

- Use Traditional Chinese.
- Keep the wording direct, instructional, and exam-oriented.
- Avoid repeating the full question text inside the explanation unless needed for clarity.
- Avoid filler phrases such as “請再多加留意”.
- Output should be a single string with visible section labels separated by line breaks.

Example target shape:

```text
答案：選項 B
作答關鍵：先抓題幹在問的核心病理或護理原則。
解析：此題正確是因為……
複習提醒：遇到這類題目先辨認……
```

## Data and Pipeline Design

No source document format change is required.

Recommended data-flow update:

1. Extract questions from the existing 7 Word files.
2. Detect whether a question already has a source note.
3. Replace the current generic fallback explanation builder with a richer standardized explanation generator.
4. Keep the final question object shape unchanged:

```python
{
  "id": "...",
  "unit": "...",
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "answer": 0,
  "explanation": "..."
}
```

This keeps `scripts/build_index.py` and the front-end data contract simple.

## UI Design

The explanation area should remain in the current answer-result position, but its content formatting should become more readable:

- preserve the existing card placement below the options
- keep the current warm note-style background
- render line breaks from the stored explanation string
- visually distinguish the label text such as `答案：` and `作答關鍵：`

If the current explanation block cannot clearly show multi-line formatted text, update the front-end rendering so the stored line breaks appear correctly.

## Behavior Rules

- Explanations continue to appear only after the learner selects an answer.
- Correct-answer behavior remains unchanged.
- Wrong-answer behavior remains unchanged.
- The `下一題` button behavior remains unchanged.
- Unit selection and session progress behavior remain unchanged.

## Error Handling

- If a question cannot be parsed into the standard explanation format, still emit a safe non-empty explanation string.
- If a source note contains unexpected punctuation or spacing, normalize it instead of dropping it.
- If a generated explanation section would be empty, fall back to a shorter but valid explanation rather than leaving blank labels.

## Testing and Verification Requirements

Implementation is not complete until all of the following are true:

- all extracted questions have non-empty explanations
- explanation coverage is 470 / 470 with no generic placeholder text remaining
- existing source-note questions still retain meaningful note content
- `index.html` rebuilds successfully from scripts
- the explanation card shows multi-line formatted content correctly
- unit selection still works
- answer feedback still works
- repository changes are committed and pushed to the user's GitHub repository

## Scope Check

This is a focused enhancement to the content-generation and presentation layers. It fits in one implementation cycle without changing the deployment model or app architecture.
