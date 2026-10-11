from fastapi.testclient import TestClient

from app.main import app
from app.services import qa_service
from app import main


def test_ask_policy_api_returns_answer_and_citations(monkeypatch):
    monkeypatch.setattr(
        main,
        "answer_policy_question",
        lambda policy_name: {
            "policy_name": policy_name,
            "answer": "Annual leave increased from 20 to 24 days.",
            "citations": [
                {
                    "section": "Annual Leave Entitlement",
                    "old_version": "v1",
                    "new_version": "v2",
                }
            ],
        },
    )

    client = TestClient(app)

    response = client.get(
        "/policies/Annual Leave Policy/ask"
    )

    assert response.status_code == 200

    data = response.json()
    assert data["policy_name"] == "Annual Leave Policy"
    assert "24 days" in data["answer"]
    assert len(data["citations"]) == 1
    assert data["citations"][0]["new_version"] == "v2"