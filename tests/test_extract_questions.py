import unittest

from scripts.extract_questions import (
    attach_notes,
    extract_all_sources,
    extract_questions_from_docx,
    fallback_explanation,
    normalize_question_id,
    parse_question_paragraph,
)


class ExtractQuestionTests(unittest.TestCase):
    def test_parse_question_paragraph_extracts_answer_and_options(self):
        parsed = parse_question_paragraph(
            "（Ｃ）12有關範例題目何者正確？(A)選項一　(B)選項二　(C)選項三　(D)選項四。(112.2.高)",
            "單元X",
        )
        self.assertEqual(parsed["unit"], "單元X")
        self.assertEqual(parsed["answer"], 2)
        self.assertEqual(parsed["question"], "有關範例題目何者正確？")
        self.assertEqual(parsed["options"], ["選項一", "選項二", "選項三", "選項四"])

    def test_parse_question_paragraph_allows_symbolic_question_index(self):
        parsed = parse_question_paragraph(
            "（Ｃ）;有關化學治療藥物作用機轉與副作用之敘述，下列何者錯誤？(A) 選項一　(B) 選項二　(C) 選項三　(D) 選項四。(111.2.高)",
            "單元X",
        )
        self.assertEqual(parsed["question"], "有關化學治療藥物作用機轉與副作用之敘述，下列何者錯誤？")

    def test_attach_notes_adds_explanation_to_previous_question(self):
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
        attach_notes(questions, "註：這是解析")
        self.assertIn("答案：A", questions[0]["explanation"])
        self.assertIn("作答關鍵：", questions[0]["explanation"])
        self.assertIn("解析：這是解析", questions[0]["explanation"])
        self.assertIn("複習提醒：", questions[0]["explanation"])

    def test_normalize_question_id_generates_stable_ids(self):
        self.assertEqual(normalize_question_id("單元5 腫瘤疾病與護理", 1), "unit5-001")

    def test_fallback_explanation_mentions_correct_option(self):
        question = {
            "question": "題目",
            "options": ["甲", "乙", "丙", "丁"],
            "answer": 1,
            "explanation": "",
        }
        text = fallback_explanation(question)
        self.assertIn("乙", text)

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

    def test_fallback_explanation_for_wrong_question_explains_question_type(self):
        question = {
            "question": "有關深部靜脈栓塞病人之護理措施，下列何者不適當？",
            "options": ["抬高患肢", "穿彈性襪", "注意肺栓塞", "按摩患肢"],
            "answer": 3,
            "explanation": "",
        }
        text = fallback_explanation(question)
        self.assertIn("題目問的是不適當", text)
        self.assertIn("按摩患肢", text)
        self.assertIn("其他選項", text)
        self.assertNotIn("最符合題幹在考的重點", text)

    def test_fallback_explanation_uses_topic_specific_nursing_guidance(self):
        question = {
            "question": "有關心衰竭病人護理指導，下列何者正確？",
            "options": ["每天量體重", "任意停用利尿劑", "高鈉飲食", "平躺可改善端坐呼吸"],
            "answer": 0,
            "explanation": "",
        }
        text = fallback_explanation(question)
        self.assertIn("體重", text)
        self.assertIn("鈉", text)
        self.assertIn("其他選項", text)

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
        self.assertIn("解析：化學治療後應注意感染徵象與血球變化", questions[0]["explanation"])
        self.assertIn("複習提醒：", questions[0]["explanation"])

    def test_extract_questions_from_docx_reads_real_source(self):
        questions = extract_questions_from_docx(
            r"C:\Users\Cyril\OneDrive\Documents\單元5 腫瘤疾病與護理.docx",
            "單元5 腫瘤疾病與護理",
        )
        self.assertGreater(len(questions), 80)
        self.assertEqual(questions[0]["id"], "unit5-001")
        self.assertEqual(len(questions[0]["options"]), 4)
        self.assertTrue(questions[5]["explanation"])

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

    def test_extract_all_sources_does_not_emit_generic_explanation_template(self):
        questions = extract_all_sources()
        combined = "\n".join(question["explanation"] for question in questions)
        self.assertNotIn("最符合題幹在考的重點", combined)
        self.assertNotIn("把題幹關鍵字與正確選項內容一一對上", combined)


if __name__ == "__main__":
    unittest.main()
