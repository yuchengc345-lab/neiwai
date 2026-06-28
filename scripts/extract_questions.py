import re
from docx import Document

ANSWER_MAP = {"Ａ": 0, "Ｂ": 1, "Ｃ": 2, "Ｄ": 3}


def parse_question_paragraph(text: str, unit: str) -> dict:
    answer_match = re.match(r"^（([Ａ-Ｄ])）", text)
    if not answer_match:
        raise ValueError(f"Unrecognized question format: {text}")

    answer = ANSWER_MAP[answer_match.group(1)]
    body = re.sub(r"^（[Ａ-Ｄ]）", "", text)
    body = body.lstrip(" 　0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ;:.,、．。-_+=~!@#$%^&*?/\\|<>[]{}()")
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
        "explanation": "",
    }


def attach_notes(questions: list[dict], note_text: str) -> None:
    if questions and note_text.startswith("註："):
        questions[-1]["explanation"] = note_text.replace("註：", "", 1).strip()


def normalize_question_id(unit: str, index: int) -> str:
    unit_number = re.search(r"單元(\d+)", unit)
    prefix = unit_number.group(1) if unit_number else "x"
    return f"unit{prefix}-{index:03d}"


def fallback_explanation(question: dict) -> str:
    correct = question["options"][question["answer"]]
    return f"本題正確答案為「{correct}」，建議回到題幹與選項關鍵字重新比對。"


def extract_questions_from_docx(path: str, unit: str) -> list[dict]:
    doc = Document(path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    questions = []

    for text in paragraphs:
        if text.startswith("（"):
            item = parse_question_paragraph(text, unit)
            item["id"] = normalize_question_id(unit, len(questions) + 1)
            questions.append(item)
        elif text.startswith("註："):
            attach_notes(questions, text)

    for item in questions:
        if not item["explanation"]:
            item["explanation"] = fallback_explanation(item)

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
