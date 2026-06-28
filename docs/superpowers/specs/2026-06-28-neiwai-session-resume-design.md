# neiwai Session Resume Design

## Summary

Add automatic session persistence to the nursing quiz app so the learner can leave the page accidentally, reopen it, and continue from the same quiz state instead of starting over.

The persistence should work entirely in the browser and keep the app deployable as a single static `index.html`.

## Goals

- Prevent accidental page exits or refreshes from resetting quiz progress.
- Restore the learner to the same unit and question after reopening the page.
- Preserve current session counters such as correct count and wrong count.
- Restore whether the current question has already been answered.
- Keep the implementation fully front-end only and compatible with GitHub Pages.

## Non-Goals

- No cross-device sync.
- No account system or backend storage.
- No history of multiple old sessions.
- No change to the existing explanation content or question data format.

## Current App State

- The quiz session exists only in runtime variables.
- Refreshing or leaving the page resets all variables.
- The app already has clear session state:
  - selected unit
  - active question list
  - current question index
  - correct count
  - wrong count
  - whether the current question has been answered
- The app already supports unit selection and restart within a selected unit.

## Recommended Approach

Use `localStorage` to persist one active quiz session snapshot in the browser.

This is preferred because:

- it survives refreshes and accidental tab closure
- it works on static hosting such as GitHub Pages
- it requires no backend or login
- it keeps the implementation small and mobile-friendly

## Persisted State

Store one JSON object representing the active quiz session, including:

- active unit identifier
- current question index
- correct count
- wrong count
- whether the current question has been answered
- selected answer index for the current question, when available
- whether the session is currently on the unit-selection screen or quiz screen

Recommended storage key:

```text
neiwai-quiz-session
```

## Restore Behavior

When the page loads:

1. Read the saved session from `localStorage`.
2. Validate that:
   - the unit still exists
   - the question index is in range
   - stored counters are numeric and non-negative
3. If valid, restore the saved session automatically.
4. If invalid, discard the saved session and fall back to the normal unit-selection screen.

If the restored question had already been answered:

- restore the disabled option state
- restore the correct/wrong coloring
- show the explanation card immediately
- keep the `下一題` button enabled

## Save Triggers

Update saved session state whenever any of the following happens:

- the user selects a unit
- the user answers a question
- the user moves to the next question
- the user restarts a unit
- the user returns to unit selection

This ensures the stored state always reflects the latest visible UI.

## Completion and Reset Rules

- When the learner finishes a unit and reaches the completion summary, clear the saved session.
- When the learner taps `重選單元`, clear the saved session.
- When the learner restarts from the completion summary, start a fresh session and save the new state from question 1.

## UI and UX Rules

- No extra settings screen is needed.
- No confirmation modal is needed for this change.
- Resume should be automatic and silent when saved state is valid.
- The visible UI should remain as simple as it is now.

## Error Handling

- If `localStorage` is unavailable or throws, the app should continue working without persistence.
- If persisted data is malformed, ignore it safely and clear that key.
- If the saved unit no longer exists, ignore the stale state and return to unit selection.

## Testing and Verification Requirements

Implementation is not complete until all of the following are true:

- selecting a unit saves session state
- answering a question saves enough state to restore the answered screen
- refreshing the page restores the current unit and question
- refreshing after answering restores option colors, explanation visibility, and next-button enabled state
- returning to unit selection clears saved state
- finishing a unit clears saved state
- the existing quiz flow still works normally when no saved state is present

## Scope Check

This is a focused front-end state persistence enhancement and fits in one implementation cycle without changing the hosting model or source question pipeline.
