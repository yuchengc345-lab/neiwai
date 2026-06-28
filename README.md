# neiwai

Single-file nursing quiz app for GitHub Pages.

## Local regeneration

```powershell
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m scripts.check_questions
& 'C:\Users\Cyril\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m scripts.build_index
```

## Files

- `index.html`: deployable single-file quiz app
- `scripts/extract_questions.py`: reads the 7 source `.docx` files and normalizes quiz data
- `scripts/build_index.py`: embeds question data into `index.html`
- `scripts/check_questions.py`: validates extracted questions

## Deploy

Push this repository to GitHub and enable GitHub Pages from the `main` branch root.
