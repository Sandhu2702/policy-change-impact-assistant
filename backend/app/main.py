from fastapi import FastAPI
from app.database.operations import get_policy_changes

app = FastAPI(
    title="Policy Change Impact Assistant",
    description="API for tracking and querying policy changes.",
    version="0.1.0",
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