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
        lambda policy_name: sample_changes,
    )

    result = qa_service.answer_policy_question(
        "Annual Leave Policy"
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
        lambda policy_name: [],
    )

    result = qa_service.answer_policy_question(
        "Unknown Policy"
    )

    assert result["citations"] == []
    assert "could not find" in result["answer"].lower()