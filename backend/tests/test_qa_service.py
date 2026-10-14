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


def test_answer_policy_question_handles_quota_error(monkeypatch):
    from google.genai import errors

    sample_changes = [
        {
            "policy_name": "Confidential Data Sharing Policy",
            "section": "AI Tools and Public Platforms",
            "change_type": "ADD",
            "old_text": "",
            "new_text": (
                "Employees must not upload confidential company "
                "information to public AI tools."
            ),
            "old_version": "v1",
            "new_version": "v2",
        }
    ]

    monkeypatch.setattr(
        qa_service,
        "retrieve_policy_evidence",
        lambda policy_name, question: sample_changes,
    )

    def raise_quota_error(prompt):
        raise errors.ClientError(
            429,
            {"error": {"message": "Quota exceeded"}},
        )

    monkeypatch.setattr(
        qa_service,
        "generate_answer",
        raise_quota_error,
    )

    result = qa_service.answer_policy_question(
        "Confidential Data Sharing Policy",
        "Can employees upload confidential information to public AI tools?",
    )

    assert "usage limit" in result["answer"].lower()
    assert len(result["citations"]) == 1
    assert result["citations"][0]["section"] == (
        "AI Tools and Public Platforms"
    )