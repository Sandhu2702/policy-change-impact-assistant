from unittest.mock import Mock, patch

import pytest
from google.genai import errors

from app.services import llm_service


def test_generate_answer_returns_response_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = Mock()
    mock_client.models.generate_content.return_value.text = "  Policy answer  "

    with patch.object(llm_service.genai, "Client", return_value=mock_client):
        result = llm_service.generate_answer("Test prompt")

    assert result == "Policy answer"
    mock_client.models.generate_content.assert_called_once()


def test_generate_answer_retries_temporary_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = Mock()
    mock_client.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"message": "Temporary outage"}}),
        Mock(text="Recovered answer"),
    ]

    with (
        patch.object(llm_service.genai, "Client", return_value=mock_client),
        patch.object(llm_service.time, "sleep"),
    ):
        result = llm_service.generate_answer("Test prompt")

    assert result == "Recovered answer"
    assert mock_client.models.generate_content.call_count == 2


def test_generate_answer_does_not_retry_permanent_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    mock_client = Mock()
    mock_client.models.generate_content.side_effect = errors.ClientError(
        400,
        {"error": {"message": "Invalid request"}},
    )

    with patch.object(llm_service.genai, "Client", return_value=mock_client):
        with pytest.raises(errors.ClientError):
            llm_service.generate_answer("Test prompt")

    mock_client.models.generate_content.assert_called_once()