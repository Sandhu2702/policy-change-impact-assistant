from app.services import qa_service


def test_answer_policy_question_with_changes(monkeypatch):
    sample_changes = [
        {
            "policy_name": "Annual Leave Policy",
            "section": "Annual Leave Entitlement",
            "change_type": "MODIFY",
            "old_text": "20 days of annual leave",
            "new_text": "24 days of annual leave",
            "old_version": "v1",
            "new_version": "v2",
        }
    ]

    monkeypatch.setattr(
        qa_service,
        "retrieve_policy_evidence",
        lambda policy_name, question: sample_changes,
    )

    monkeypatch.setattr(
        qa_service,
        "generate_answer",
        lambda prompt: (
            "Annual leave increased from 20 days to 24 days."
        ),
    )

    result = qa_service.answer_policy_question(
        "Annual Leave Policy",
        "How many annual leave days are allowed?",
    )

    assert "20 days" in result["answer"]
    assert "24 days" in result["answer"]
    assert len(result["citations"]) == 1
    assert result["citations"][0]["section"] == (
        "Annual Leave Entitlement"
    )


def test_answer_policy_question_without_changes(monkeypatch):
    monkeypatch.setattr(
        qa_service,
        "retrieve_policy_evidence",
        lambda policy_name, question: [],
    )

    result = qa_service.answer_policy_question(
        "Unknown Policy",
        "What changed?",
    )

    assert result["citations"] == []
    assert "could not find" in result["answer"].lower()


def retrieve_policy_evidence(
    policy_name: str,
    question: str,
) -> list[dict]:
    """Retrieve saved changes relevant to the user's question."""
    changes = get_policy_changes(policy_name=policy_name)

    stop_words = {
        "what", "is", "the", "how", "many", "are",
        "a", "an", "in", "of", "to", "for", "and",
        "does", "do", "was", "were", "with", "changed",
        "can", "they", "their", "whether", "under",
        "allowed", "whether",
    }

    question_words = {
        word.strip(".,?!:;()")
        for word in question.lower().split()
        if word.strip(".,?!:;()") not in stop_words
    }

    relevant_changes = []

    for change in changes:
        searchable_text = " ".join([
            change["section"] or "",
            change["old_text"] or "",
            change["new_text"] or "",
        ]).lower()

        searchable_words = set(searchable_text.split())

        matched_words = question_words.intersection(searchable_words)

        if matched_words:
            relevant_changes.append((len(matched_words), change))

    if not relevant_changes:
        return []

    relevant_changes.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    highest_score = relevant_changes[0][0]

    return [
        change
        for score, change in relevant_changes
        if score == highest_score
    ]