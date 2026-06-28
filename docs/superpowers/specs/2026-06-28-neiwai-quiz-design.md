# neiwai Quiz App Design

## Summary

Build a GitHub-ready, mobile-first quiz web app for nursing practice questions using a single deployable `index.html` file.

The first release covers exactly 7 source documents:

- `單元5 腫瘤疾病與護理.docx`
- `單元7 呼吸系統疾病與護理1.docx`
- `單元8 呼吸系統疾病與護理2.docx`
- `單元9 呼吸系統疾病與護理3.docx`
- `單元10 心臟血管系統疾病與護理1.docx`
- `單元11 心臟血管系統疾病與護理2.docx`
- `單元12 心臟血管系統疾病與護理3.docx`

The app is intended to run as a static site on GitHub Pages, with no backend, no build step, and no dependency installation required for end users.

## Goals

- Ship a single-file quiz app that can be opened locally or hosted on GitHub Pages.
- Optimize for phone usage first, while still displaying cleanly on desktop.
- Support single-choice questions only.
- Provide immediate answer feedback, visual correctness states, and explanation display.
- Track progress clearly during a session.
- Convert the 7 provided Word documents into a uniform quiz data structure for the first release.
- Prepare the repository so it can be pushed to the user's GitHub repository `yuchengc345-lab/neiwai`.

## Non-Goals

- No user accounts, cloud sync, or backend storage.
- No timed quiz mode in the first release.
- No multi-select questions in the first release.
- No server-side parsing of Word documents in production.
- No admin UI for uploading new question files in the first release.

## Current Evidence

- The current workspace directory is not yet a git repository.
- The provided 7 `.docx` files are available outside the workspace and readable.
- The 7 documents contain about 470 question-like entries in a mostly uniform format.
- Most questions are contained in one paragraph each.
- Some questions are followed by a `註：...` paragraph that should be treated as explanation content for the preceding question.

## Product Shape

The repository will contain:

- `index.html`: the full deployable app, including HTML, CSS, JavaScript, and the final `questions` array
- optional helper scripts used during development only to extract and normalize question data from the source `.docx` files
- optional documentation for data regeneration and deployment

The deployed app remains a single static HTML page.

## App Behavior

### Session Flow

1. The user opens the page and starts on the first question.
2. The page shows the current unit label, question number, progress bar, and cumulative correct and wrong counts.
3. The user taps one option.
4. The app immediately locks all options for that question.
5. If the chosen option is correct, that option turns green.
6. If the chosen option is incorrect, the chosen option turns red and the correct option turns green.
7. The explanation panel appears immediately after answering.
8. The `下一題` button becomes enabled only after the question has been answered.
9. The user advances through all questions in sequence.
10. On the last question, the app shows a completion state with summary statistics and a restart action.

### Progress and Scoring

- Show `第 X / Y 題` in a prominent location.
- Show a horizontal progress bar based on answered question count.
- Show at least the current wrong-count and correct-count.
- Track session state in memory.
- Do not persist session state across refreshes in the first release.

### Explanation Rules

- If a question has an adjacent `註：...` paragraph in the source material, use that as the explanation body.
- If no explanation exists in the source material, generate a short fallback explanation based on the correct option text, clearly as a generic explanation rather than invented textbook detail.
- The explanation panel should always appear after answering so the interaction stays consistent.

## Content and Data Model

### Final Runtime Data Structure

The front-end runtime uses:

```js
const questions = [
  {
    id: "unit5-001",
    unit: "單元5 腫瘤疾病與護理",
    question: "題目文字",
    options: ["A", "B", "C", "D"],
    answer: 3,
    explanation: "解析文字"
  }
];
```

### Source Parsing Rules

- Detect the correct answer from the full-width marker at the beginning of the paragraph, such as `（Ａ）` through `（Ｄ）`.
- Extract the question stem and the four answer options from inline `(A)`, `(B)`, `(C)`, `(D)` segments.
- Preserve important clinical wording and punctuation from the original document.
- Strip exam metadata like year or exam source suffixes from the visible question text only if removal improves readability without losing study value.
- Associate a following `註：...` paragraph with the immediately preceding question.
- Manually patch edge cases where OCR-like characters or formatting irregularities break parsing.

### Data Quality Strategy

- Prefer deterministic parsing first.
- Review failed or suspicious parses manually.
- Keep a clear separation between extraction-time cleanup and runtime app logic.
- Preserve source order within each unit.

## Visual Design

### Direction

The interface should feel calm, focused, and tactile rather than like a generic dashboard.

Visual system:

- warm light background with subtle depth
- blue as the primary interface color
- green for correct answers
- red for incorrect answers
- a muted card tone for explanations
- rounded cards sized for thumb interaction

### Layout

- Single-column layout centered within a narrow mobile reading width
- Sticky or top-priority progress area
- Large question card
- Four stacked option cards
- Explanation card below options
- Large bottom action button with safe spacing for thumb reach

### Interaction

- Option cards have light elevation and border definition
- Tap feedback uses a small scale or press animation
- Disabled state is obvious after answer submission
- Motion should be brief and purposeful, not decorative

## Technical Architecture

### Deployment Form

- Static site
- No framework requirement
- No bundler requirement
- Final deploy target is GitHub Pages

### Development Form

During development, it is acceptable to use:

- one or more local helper scripts to parse `.docx`
- a temporary generated data artifact before embedding questions into `index.html`

These helpers are not required for runtime.

### Front-End Structure Inside `index.html`

- semantic HTML shell
- embedded CSS with design tokens in `:root`
- embedded JavaScript for:
  - app state
  - rendering current question
  - answer handling
  - progress updates
  - next-question navigation
  - restart handling

## Error Handling

- If a question is malformed and cannot be rendered safely, it should be excluded during data preparation rather than fail at runtime.
- If explanation text is missing, display a fallback explanation message.
- If the question set is empty, show a friendly empty-state message instead of a broken layout.

## Verification Plan

Implementation will not be considered complete until these checks pass:

- the generated `index.html` opens locally without a build step
- question selection behavior matches the approved interaction rules
- `下一題` stays disabled until answering
- progress counts update correctly
- the final question transitions to a completion state
- the page remains usable on a narrow mobile viewport
- the site structure is compatible with GitHub Pages static hosting
- the repo contains the files needed to publish to `yuchengc345-lab/neiwai`

## Repository and Publish Plan

Once implementation begins:

1. Initialize or connect the local workspace to the target GitHub repository.
2. Add the single-file app and any minimal supporting files.
3. Verify the static site locally.
4. Commit intentionally.
5. Push to GitHub.
6. Enable or verify GitHub Pages.
7. Return the public link to the user.

## Open Constraints

- The current workspace is not yet attached to the target git repository.
- The design doc cannot be committed yet because the local workspace is not currently a git repository.
- Pushing to GitHub and enabling Pages may require authentication or explicit approval depending on the local environment state.
- Because the source documents live outside the workspace root, development helpers must read them without mutating them.

## Scope Check

This spec is intentionally limited to the first release:

- 7 source documents only
- single-file runtime app
- static GitHub Pages deployment
- no extra study modes

This is small enough for one implementation plan and one delivery cycle.
