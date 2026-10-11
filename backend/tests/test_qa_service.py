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


def test_retrieve_policy_evidence_matches_relevant_words(monkeypatch):
    sample_changes = [
        {
            "policy_name": "Annual Leave Policy",
            "section": "Annual Leave Entitlement",
            "change_type": "MODIFY",
            "old_text": "20 days of annual leave",
            "new_text": "24 days of annual leave",
            "old_version": "v1",
            "new_version": "v2",
        },
        {
            "policy_name": "Annual Leave Policy",
            "section": "Leave Application Process",
            "change_type": "MODIFY",
            "old_text": "Apply 7 days in advance",
            "new_text": "Apply 14 days in advance",
            "old_version": "v1",
            "new_version": "v2",
        },
    ]

    monkeypatch.setattr(
        qa_service,
        "get_policy_changes",
        lambda policy_name: sample_changes,
    )

    result = qa_service.retrieve_policy_evidence(
        "Annual Leave Policy",
        "How many annual leave days are allowed?",
    )

    assert len(result) == 1
    assert result[0]["section"] == "Annual Leave Entitlement"