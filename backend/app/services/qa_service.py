from app.database.operations import get_policy_changes


def retrieve_policy_evidence(
    policy_name: str,
) -> list[dict]:
    """Retrieve saved changes to use as evidence for an answer."""
    return get_policy_changes(policy_name=policy_name)


def answer_policy_question(
    policy_name: str,
) -> dict:
    """Create a basic answer using saved policy changes."""
    changes = retrieve_policy_evidence(policy_name)

    if not changes:
        return {
            "policy_name": policy_name,
            "answer": (
                "I could not find saved changes for this policy."
            ),
            "citations": [],
        }

    summaries = []
    citations = []

    for change in changes:
        if change["change_type"] == "ADD":
            summaries.append(
                f"Added in {change['new_version']}: "
                f"{change['new_text']}"
            )
        elif change["change_type"] == "REMOVE":
            summaries.append(
                f"Removed in {change['new_version']}: "
                f"{change['old_text']}"
            )
        else:
            summaries.append(
                f"Changed from '{change['old_text']}' "
                f"to '{change['new_text']}' "
                f"in {change['new_version']}."
            )

        citations.append({
            "section": change["section"],
            "old_version": change["old_version"],
            "new_version": change["new_version"],
        })

    return {
        "policy_name": policy_name,
        "answer": " ".join(summaries),
        "citations": citations,
    }