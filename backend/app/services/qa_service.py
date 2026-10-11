from app.database.operations import get_policy_changes


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

        matched_words = [
            word for word in question_words
            if word in searchable_text
        ]

        if matched_words:
            relevant_changes.append((len(matched_words), change))

        relevant_changes.sort(key=lambda item: item[0], reverse=True)

        return [change for _, change in relevant_changes]

    return relevant_changes


def answer_policy_question(
    policy_name: str,
    question: str,
) -> dict:
    """Create a basic answer using saved policy changes."""
    changes = retrieve_policy_evidence(policy_name, question)

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