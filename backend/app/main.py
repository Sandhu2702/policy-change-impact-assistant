from fastapi import FastAPI, Query
from app.database.operations import get_policy_changes
from app.services.policy_service import process_policy_versions
from app.services.qa_service import answer_policy_question
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Policy Change Impact Assistant",
    description="API for tracking and querying policy changes.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Policy Change Impact Assistant API is running",
    }

@app.get("/policies/{policy_name}/changes")
def get_changes(
    policy_name: str,
    old_version: str | None = None,
    new_version: str | None = None,
):
    """Return saved changes for a policy."""
    changes = get_policy_changes(
        policy_name=policy_name,
        old_version=old_version,
        new_version=new_version,
    )

    return {
        "policy_name": policy_name,
        "count": len(changes),
        "changes": changes,
    }


@app.post("/policies/{policy_name}/compare")
def compare_policy_versions(
    policy_name: str,
    old_version: str,
    new_version: str,
    old_file_path: str,
    new_file_path: str,
):
    """Compare two policy versions and save their changes."""

    changes = process_policy_versions(
        policy_name=policy_name,
        old_version=old_version,
        new_version=new_version,
        old_file_path=old_file_path,
        new_file_path=new_file_path,
    )

    return {
        "policy_name": policy_name,
        "old_version": old_version,
        "new_version": new_version,
        "count": len(changes),
        "changes": changes,
    }


@app.get("/policies/{policy_name}/ask")
def ask_policy_question(
    policy_name: str,
    question: str = Query(..., min_length=3),
):
    """Answer a question using saved policy changes."""
    return answer_policy_question(
        policy_name=policy_name,
        question=question,
    )