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


def normalize_question_id(unit: str, index: int) -> str:
    unit_number = re.search(r"單元(\d+)", unit)
    prefix = unit_number.group(1) if unit_number else "x"
    return f"unit{prefix}-{index:03d}"


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


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword.lower() in text.lower() for keyword in keywords)


def question_mode_guidance(question_text: str) -> tuple[str, str, str]:
    if contains_any(question_text, ("不適當", "不宜", "不應", "不可", "不能", "禁忌")):
        return (
            "題目問的是不適當或不可採用的敘述，要反向作答，找出最需要避免的選項。",
            "題目問的是不適當，因此正確答案代表臨床上不應採取、需排除或與原則相反的內容。",
            "看到「不適當／不宜／不可」時，先把題目轉成「哪一項不能做」，再判斷安全性。",
        )
    if contains_any(question_text, ("錯誤", "不正確")):
        return (
            "題目問的是錯誤敘述，要找出與疾病機轉、檢查或護理原則不一致的選項。",
            "題目問的是錯誤，因此正確答案不是要照做，而是指出該敘述與臨床概念不符。",
            "遇到「錯誤／不正確」題，先標記否定字，避免把正確照護原則誤選掉。",
        )
    if contains_any(question_text, ("最優先", "優先", "首先", "立即")):
        return (
            "題目考優先順序，先處理會威脅生命或造成病情快速惡化的問題。",
            "優先題要以 ABC、循環穩定、安全風險與急性變化來排序，而不是只選看起來常見的照護。",
            "優先題先問自己：哪一項不先做會最快造成危險。",
        )
    if contains_any(question_text, ("正確", "適當", "最可能", "最佳", "應")):
        return (
            "題目問正確或適當作法，要選出最符合病理機轉、檢查目的與護理安全的選項。",
            "這類題要把題幹情境與選項逐一比對，選出最符合照護原則的一項。",
            "作答時優先抓疾病關鍵字，再排除與安全、藥物或檢查原則相衝突的選項。",
        )
    return (
        "先判斷題幹是在考定義、症狀、檢查、治療或護理措施，再回到選項比對。",
        "本題重點在辨認題幹所描述的核心概念，答案要能直接解釋題幹情境。",
        "複習時把題目整理成「病因／表現／檢查／治療／護理」其中一類，會更容易判斷。",
    )


def topic_guidance(question: dict, correct: str) -> tuple[str, str, str]:
    haystack = " ".join(
        [
            question.get("unit", ""),
            question.get("question", ""),
            correct,
            " ".join(question.get("options", [])),
        ]
    )
    rules = [
        (
            ("心衰竭", "心臟衰竭", "肺水腫", "端坐呼吸", "利尿", "體重", "水腫"),
            "心衰竭題要分辨左心衰竭的肺部鬱血與右心衰竭的全身靜脈鬱血。",
            "心衰竭護理重點包括每日同一時間量體重、評估呼吸困難與水腫、限制鈉與水分、依醫囑使用利尿劑並監測電解質。",
            "看到體重突然上升、端坐呼吸、濕囉音或下肢水腫，要想到體液滯留與心衰竭惡化。",
        ),
        (
            ("心肌梗塞", "心絞痛", "胸痛", "硝酸甘油", "nitroglycerin", "troponin", "ST"),
            "缺血性心臟病題要先判斷疼痛型態、是否休息可緩解，以及是否已有心肌壞死證據。",
            "心絞痛多與暫時性心肌缺氧有關；心肌梗塞則代表心肌壞死，常需評估心電圖、心肌酵素與持續胸痛，護理上要重視氧合、疼痛、生命徵象與再灌流時機。",
            "胸痛題先抓「持續時間、休息或硝酸甘油是否緩解、心電圖與酵素變化」。",
        ),
        (
            ("digoxin", "毛地黃", "地高辛"),
            "Digoxin 題要連到心尖脈、心搏過慢、血鉀與中毒症狀。",
            "給 Digoxin 前需評估心尖脈，若心搏過慢要暫緩並通知醫師；低血鉀會增加毒性風險，噁心、嘔吐、視覺異常與心律不整都是警訊。",
            "記住 Digoxin：先量心尖脈，再看鉀離子與中毒表現。",
        ),
        (
            ("warfarin", "可邁丁", "coumadin", "PT", "INR"),
            "Warfarin 題要抓凝血監測與出血安全。",
            "Warfarin 主要以 PT/INR 追蹤抗凝效果，需注意牙齦出血、血尿、黑便、瘀青等出血徵象；維生素 K 攝取需穩定，不是完全禁食。",
            "抗凝藥題看到 Warfarin 就想到 PT/INR、出血觀察與維生素 K。",
        ),
        (
            ("heparin", "肝素", "aPTT", "protamine"),
            "Heparin 題要抓 aPTT 監測與拮抗劑。",
            "Heparin 常以 aPTT 監測抗凝效果，主要風險是出血；發生嚴重出血時常用 protamine sulfate 作為拮抗劑。",
            "抗凝藥題先分清楚：Heparin 看 aPTT，Warfarin 看 PT/INR。",
        ),
        (
            ("深部靜脈", "DVT", "肺栓塞", "Homan", "血栓", "栓塞"),
            "深部靜脈栓塞題要連到血栓脫落與肺栓塞風險。",
            "DVT 照護重點是觀察腫脹疼痛、避免按摩患肢、依醫囑抗凝、促進安全活動並警覺突發呼吸困難或胸痛等肺栓塞徵象。",
            "看到 DVT 或 Homan sign，最怕的是血栓脫落；按摩患肢通常是危險干擾項。",
        ),
        (
            ("高血壓", "血壓", "降壓"),
            "高血壓題要抓長期控制、器官損傷與服藥遵從性。",
            "高血壓護理強調規律服藥、低鈉飲食、體重控制、運動、戒菸限酒與定期量血壓；即使症狀改善也不應自行停藥。",
            "高血壓常考「無症狀也要治療」與「不可自行停藥」。",
        ),
        (
            ("心導管", "冠狀動脈攝影", "穿刺", "股動脈"),
            "心導管題要注意穿刺部位出血與遠端循環。",
            "心導管術後需觀察穿刺處有無出血、血腫，評估遠端脈搏、膚色、溫度與感覺，並依穿刺部位維持臥床與肢體伸直。",
            "術後題先看出血、循環、疼痛與生命徵象變化。",
        ),
        (
            ("動脈硬化", "周邊動脈", "間歇性跛行", "缺血", "足背動脈"),
            "周邊動脈疾病題要抓組織灌流不足。",
            "動脈灌流不足常見肢端冰冷、蒼白、疼痛、脈搏減弱與間歇性跛行；照護重點是戒菸、規律步行訓練、保護足部並避免受傷。",
            "動脈問題記「冷、痛、白、脈弱」；靜脈問題多是腫脹、沉重與色素沉著。",
        ),
        (
            ("靜脈曲張", "靜脈功能", "靜脈鬱積", "彈性襪"),
            "靜脈疾病題要抓回流不良與壓力治療。",
            "靜脈回流不良常以抬高患肢、彈性襪、避免久站久坐與促進小腿肌肉收縮改善；重點是減少鬱血與水腫。",
            "靜脈照護常考彈性襪、抬腿、避免久站與皮膚保護。",
        ),
        (
            ("主動脈瘤", "腹主動脈瘤", "動脈瘤"),
            "主動脈瘤題要抓破裂風險與血壓控制。",
            "主動脈瘤需觀察腹背痛、搏動性腫塊、低血壓或休克等破裂徵象；護理上要避免增加腹壓並控制血壓，突發劇痛是危急警訊。",
            "動脈瘤題看到突發腹痛、背痛、休克，要優先想到破裂。",
        ),
        (
            ("氣喘", "哮喘", "喘鳴", "支氣管痙攣", "尖峰呼氣流速"),
            "氣喘題要抓支氣管收縮、發炎與可逆性呼氣氣流受限。",
            "氣喘急性發作常有喘鳴、呼氣延長與呼吸困難，護理重點是評估呼吸音與尖峰呼氣流速、避免誘發因子、依醫囑使用支氣管擴張劑與抗發炎藥物。",
            "氣喘常考短效支氣管擴張劑、誘發因子與發作時呼氣困難。",
        ),
        (
            ("COPD", "肺氣腫", "慢性支氣管炎", "噘嘴", "二氧化碳", "CO2"),
            "COPD 題要抓慢性氣流受限、換氣效率差與呼吸訓練。",
            "COPD 護理重點是戒菸、噘嘴式呼吸、活動耐受訓練、營養支持與依醫囑給氧；若有 CO2 滯留風險，氧療需謹慎監測。",
            "COPD 常考噘嘴式呼吸、低流量氧氣與避免呼吸抑制。",
        ),
        (
            ("肺炎", "痰", "咳嗽", "發燒", "抗生素"),
            "肺炎題要抓感染、痰液清除與氧合。",
            "肺炎照護包括評估發燒、咳嗽、痰液性質、呼吸音與血氧，鼓勵深呼吸咳嗽、補充水分、依醫囑使用抗生素並觀察療效。",
            "肺炎題常用「感染徵象＋呼吸評估＋促進排痰」來判斷。",
        ),
        (
            ("結核", "TB", "抗酸菌", "空氣隔離", "負壓", "N95"),
            "肺結核題要抓空氣傳染與完整服藥。",
            "肺結核需採空氣傳染防護，常見措施包括負壓病室、N95 防護與規則完成多重抗結核藥物療程，避免因症狀改善就停藥。",
            "TB 題記住空氣隔離、N95、負壓與服藥完整性。",
        ),
        (
            ("氣胸", "胸管", "水封瓶", "胸腔引流", "皮下氣腫"),
            "氣胸與胸管題要抓胸腔壓力、引流系統與呼吸惡化。",
            "胸管照護需保持系統低於胸腔、避免管路扭曲或牽拉、觀察水封波動與氣泡、評估引流量與呼吸狀態；不可任意夾管或抬高引流瓶。",
            "胸管題先看位置、密閉性、波動氣泡與病人呼吸狀態。",
        ),
        (
            ("ARDS", "急性呼吸窘迫", "PEEP", "俯臥"),
            "ARDS 題要抓頑固性低血氧與肺泡塌陷。",
            "ARDS 常見嚴重低血氧、瀰漫性肺泡損傷與肺順應性下降；治療照護常涉及氧合支持、PEEP、俯臥位與密切監測呼吸循環。",
            "ARDS 的關鍵字是「氧氣給了仍低氧」與需要進階呼吸支持。",
        ),
        (
            ("肺栓塞", "栓塞", "突發呼吸困難"),
            "肺栓塞題要抓突發呼吸困難、胸痛與低氧。",
            "肺栓塞常表現為突發呼吸困難、胸痛、心搏過速、低血氧或咳血，常與 DVT 有關；護理上要立即評估呼吸循環並依醫囑抗凝或進一步處置。",
            "突發呼吸困難加胸痛，尤其合併 DVT 風險，要想到肺栓塞。",
        ),
        (
            ("化學治療", "化療", "白血球", "嗜中性球", "骨髓抑制", "掉髮"),
            "化學治療題要抓骨髓抑制、感染風險與副作用處理。",
            "化療常見骨髓抑制、噁心嘔吐、黏膜炎、掉髮與疲倦；護理上要監測血球數、感染與出血徵象，並教導口腔照護與避免感染暴露。",
            "化療題看到發燒、白血球低或血小板低，要立刻想到感染與出血風險。",
        ),
        (
            ("放射線", "放射治療", "電療", "照射"),
            "放射治療題要抓局部皮膚照護與疲倦。",
            "放射治療照護重點是保護照射部位皮膚，避免摩擦、抓癢、熱敷、冰敷或自行塗刺激性藥膏，並評估疲倦與局部組織反應。",
            "放療皮膚題記住：溫和清潔、避免刺激、不要任意塗抹或摩擦。",
        ),
        (
            ("腫瘤標記", "PSA", "AFP", "CEA", "CA-125", "CA125", "CA15-3", "CA19-9"),
            "腫瘤標記題要把標記物和常見癌別連起來。",
            "常見配對包括 PSA 與攝護腺、AFP 與肝癌或生殖細胞腫瘤、CEA 與大腸直腸癌追蹤、CA-125 與卵巢癌、CA15-3 與乳癌、CA19-9 與胰臟或膽道相關腫瘤。",
            "腫瘤標記多用於輔助診斷與追蹤，不宜單獨當作唯一診斷依據。",
        ),
        (
            ("良性", "惡性", "轉移", "分化", "接觸抑制", "腫瘤", "癌"),
            "腫瘤概念題要分清良惡性、侵犯性與轉移能力。",
            "良性腫瘤多生長較慢、邊界較清楚且不轉移；惡性腫瘤常侵犯周邊組織、分化較差且可能經血液或淋巴轉移，癌細胞也常失去正常接觸抑制。",
            "腫瘤題常考「侵犯、轉移、分化差、接觸抑制消失」。",
        ),
    ]
    for keywords, clue, detail, reminder in rules:
        if contains_any(haystack, keywords):
            return clue, detail, reminder
    return (
        "把題幹歸類到疾病表現、檢查判讀、藥物安全或護理措施，再用臨床安全原則排除干擾項。",
        "本題要從題幹情境判斷最合適的臨床概念；作答時不只看單一字眼，也要看選項是否符合病人安全、疾病機轉與照護優先順序。",
        "複習時把同類題整理成「關鍵症狀、危險徵象、檢查指標、護理禁忌」四欄，會比背單題更穩。",
    )


def contrast_guidance(question_text: str, incorrect_options: list[str]) -> str:
    sample_options = "、".join(option for option in incorrect_options[:2] if option)
    prefix = f"其他選項如「{sample_options}」" if sample_options else "其他選項"
    if contains_any(question_text, ("不適當", "不宜", "不應", "不可", "不能", "禁忌", "錯誤", "不正確")):
        return f"{prefix}多半代表較符合原則的敘述或較不危險的作法；本題真正要抓的是哪一項需要排除。"
    return f"{prefix}是干擾項，常見問題是太絕對、偏離題幹情境，或與病人安全及照護原則不一致。"


def fallback_explanation(question: dict) -> str:
    correct = question["options"][question["answer"]]
    incorrect_options = [
        option for index, option in enumerate(question["options"]) if index != question["answer"]
    ]
    mode_clue, mode_detail, mode_reminder = question_mode_guidance(question["question"])
    topic_clue, topic_detail, topic_reminder = topic_guidance(question, correct)
    contrast = contrast_guidance(question["question"], incorrect_options)
    return build_explanation(
        answer_text=correct,
        clue_text=f"{mode_clue} 本題答案指向「{correct}」；{topic_clue}",
        detail_text=f"{mode_detail} 「{correct}」之所以是答案，是因為它符合本題核心判斷。{topic_detail} {contrast}",
        reminder_text=f"{topic_reminder} {mode_reminder}",
    )


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
