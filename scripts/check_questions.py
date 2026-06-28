from scripts.extract_questions import extract_all_sources


def main() -> None:
    questions = extract_all_sources()
    assert questions, "No questions extracted"
    for item in questions:
        assert item["question"].strip(), f"Empty question: {item['id']}"
        assert len(item["options"]) == 4, f"Option count error: {item['id']}"
        assert 0 <= item["answer"] <= 3, f"Answer range error: {item['id']}"
        assert item["explanation"].strip(), f"Missing explanation: {item['id']}"
    print(f"Validated {len(questions)} questions")


if __name__ == "__main__":
    main()
