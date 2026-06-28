import json
from pathlib import Path

from scripts.extract_questions import extract_all_sources


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
      --surface: rgba(255, 255, 255, 0.9);
      --line: #d5dde8;
      --text: #18324d;
      --muted: #6d7f95;
      --blue: #4b86d4;
      --green: #37a86e;
      --red: #dc6e64;
      --note: #fff8de;
      --shadow: 0 14px 32px rgba(24, 50, 77, 0.09);
      --radius: 22px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top, rgba(75, 134, 212, 0.18), transparent 30%),
        linear-gradient(180deg, #f8f4ee 0%, #edf4fb 100%);
      min-height: 100vh;
    }}
    .shell {{
      width: min(100%, 760px);
      margin: 0 auto;
      padding: 16px 16px 36px;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid rgba(255, 255, 255, 0.7);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}
    .progress-panel {{
      position: sticky;
      top: 0;
      z-index: 2;
      padding: 16px;
    }}
    .meta-top {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      font-size: 14px;
    }}
    .unit-label {{
      margin-top: 8px;
      font-size: 15px;
      font-weight: 700;
      color: var(--blue);
    }}
    .progress-copy {{
      margin-top: 8px;
      font-size: 19px;
      font-weight: 800;
    }}
    .scoreboard {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .progress-bar {{
      margin-top: 12px;
      height: 10px;
      background: #dfe8f2;
      border-radius: 999px;
      overflow: hidden;
    }}
    .progress-fill {{
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, #5c98df, #37a86e);
      transition: width 0.18s ease;
    }}
    .question-panel {{
      margin-top: 16px;
      padding: 18px;
    }}
    .question-text {{
      margin: 0;
      line-height: 1.7;
      font-size: 20px;
    }}
    .options {{
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }}
    .option {{
      width: 100%;
      border: 1px solid var(--line);
      background: #fff;
      color: var(--text);
      border-radius: 18px;
      padding: 16px;
      text-align: left;
      font-size: 16px;
      line-height: 1.6;
      box-shadow: 0 5px 14px rgba(24, 50, 77, 0.04);
      transition: transform 0.12s ease, border-color 0.12s ease, background 0.12s ease;
    }}
    .option:active {{
      transform: scale(0.985);
    }}
    .option.correct {{
      background: #e8f7ee;
      border-color: var(--green);
      color: #155638;
    }}
    .option.wrong {{
      background: #fdeceb;
      border-color: var(--red);
      color: #8b2d28;
    }}
    .option:disabled {{
      opacity: 1;
    }}
    .explanation {{
      display: none;
      margin-top: 16px;
      padding: 16px;
      border-radius: 18px;
      border: 1px solid #f0dd9c;
      background: var(--note);
      line-height: 1.75;
    }}
    .explanation.show {{
      display: block;
    }}
    .explanation-title {{
      font-weight: 800;
    }}
    .explanation-text {{
      margin: 8px 0 0;
    }}
    .next-button {{
      width: 100%;
      margin-top: 18px;
      border: none;
      border-radius: 18px;
      padding: 16px;
      font-size: 17px;
      font-weight: 800;
      color: #f8fbff;
      background: #b9cade;
      transition: transform 0.12s ease, opacity 0.12s ease;
    }}
    .next-button.enabled {{
      background: linear-gradient(135deg, #4c88d6, #2f6ec7);
    }}
    .next-button:active {{
      transform: scale(0.99);
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="panel progress-panel">
      <div class="meta-top">
        <span>護理刷題</span>
        <span id="session-status">本輪進行中</span>
      </div>
      <div id="unit-label" class="unit-label"></div>
      <div class="progress-copy">第 <span id="current-number">1</span> / <span id="total-number">1</span> 題</div>
      <div class="scoreboard">答對 <span id="correct-count">0</span> · 錯題 <span id="wrong-count">0</span></div>
      <div class="progress-bar"><div id="progress-fill" class="progress-fill"></div></div>
    </section>
    <section class="panel question-panel">
      <h1 id="question-text" class="question-text"></h1>
      <div id="options" class="options"></div>
      <section id="explanation" class="explanation">
        <div class="explanation-title">解析</div>
        <p id="explanation-text" class="explanation-text"></p>
      </section>
      <button id="next-button" class="next-button" disabled>下一題</button>
    </section>
  </main>
  <script>
    const questions = {data};
    let currentIndex = 0;
    let correctCount = 0;
    let wrongCount = 0;
    let answeredCurrent = false;

    const unitLabel = document.getElementById('unit-label');
    const sessionStatus = document.getElementById('session-status');
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

    function updateProgress() {{
      currentNumber.textContent = String(Math.min(currentIndex + 1, Math.max(questions.length, 1)));
      totalNumber.textContent = String(questions.length);
      correctCountNode.textContent = String(correctCount);
      wrongCountNode.textContent = String(wrongCount);
      const ratio = questions.length ? (currentIndex / questions.length) * 100 : 0;
      progressFill.style.width = `${{ratio}}%`;
      nextButton.disabled = !answeredCurrent;
      nextButton.classList.toggle('enabled', answeredCurrent);
    }}

    function renderQuestion() {{
      const item = questions[currentIndex];
      answeredCurrent = false;
      sessionStatus.textContent = '本輪進行中';
      unitLabel.textContent = item.unit;
      questionText.textContent = item.question;
      explanationText.textContent = item.explanation;
      explanation.classList.remove('show');
      options.innerHTML = '';
      item.options.forEach((label, index) => {{
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'option';
        button.textContent = `${{String.fromCharCode(65 + index)}}. ${{label}}`;
        button.addEventListener('click', () => handleAnswer(index));
        options.appendChild(button);
      }});
      nextButton.textContent = '下一題';
      updateProgress();
    }}

    function handleAnswer(selectedIndex) {{
      if (answeredCurrent) return;
      answeredCurrent = true;
      const item = questions[currentIndex];
      const buttons = [...options.querySelectorAll('.option')];
      buttons.forEach((button) => {{
        button.disabled = true;
      }});
      if (selectedIndex === item.answer) {{
        correctCount += 1;
        buttons[selectedIndex].classList.add('correct');
      }} else {{
        wrongCount += 1;
        buttons[selectedIndex].classList.add('wrong');
        buttons[item.answer].classList.add('correct');
      }}
      explanation.classList.add('show');
      updateProgress();
    }}

    function showCompletion() {{
      sessionStatus.textContent = '本輪完成';
      unitLabel.textContent = '完成';
      questionText.textContent = `你已完成 ${{questions.length}} 題`;
      options.innerHTML = '';
      answeredCurrent = true;
      explanation.classList.add('show');
      explanationText.textContent = `答對 ${{correctCount}} 題，錯題 ${{wrongCount}} 題。按下方按鈕可重新開始。`;
      nextButton.textContent = '重新開始';
      nextButton.disabled = false;
      nextButton.classList.add('enabled');
      progressFill.style.width = '100%';
    }}

    nextButton.addEventListener('click', () => {{
      if (!answeredCurrent && questions.length) return;
      if (!questions.length) return;
      if (currentIndex === questions.length - 1 && nextButton.textContent === '下一題') {{
        showCompletion();
        return;
      }}
      if (nextButton.textContent === '重新開始') {{
        currentIndex = 0;
        correctCount = 0;
        wrongCount = 0;
        renderQuestion();
        return;
      }}
      currentIndex += 1;
      renderQuestion();
    }});

    if (questions.length) {{
      renderQuestion();
    }} else {{
      sessionStatus.textContent = '目前沒有題目';
      unitLabel.textContent = '題庫未載入';
      questionText.textContent = '請先確認題庫是否已成功匯入。';
      nextButton.style.display = 'none';
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    html = render_index(extract_all_sources())
    Path("index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
