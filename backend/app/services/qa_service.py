from app.database.operations import get_policy_changes
from app.services.llm_service import generate_answer

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
            if word in searchable_text.split()
        ]

        if matched_words:
            relevant_changes.append((len(matched_words), change))

    relevant_changes.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [change for _, change in relevant_changes]


def answer_policy_question(
    policy_name: str,
    question: str,
) -> dict:
    """Answer a policy question using retrieved evidence and Gemini."""
    changes = retrieve_policy_evidence(policy_name, question)

    if not changes:
        return {
            "policy_name": policy_name,
            "answer": (
                "I could not find relevant saved changes "
                "to answer this question."
            ),
            "citations": [],
        }

    evidence = []

    for change in changes:
        evidence.append({
            "section": change["section"],
            "change_type": change["change_type"],
            "old_text": change["old_text"],
            "new_text": change["new_text"],
            "old_version": change["old_version"],
            "new_version": change["new_version"],
        })

    prompt = f"""
You are a careful Policy Change Impact Assistant.

Policy: {policy_name}
User question: {question}

Retrieved policy-change evidence:
{evidence}

Instructions:
- Answer the user's question using only the supplied evidence.
- Do not invent policy rules, dates, amounts, or requirements.
- If the evidence does not contain enough information, clearly say so.
- Distinguish old policy text from new policy text.
- Explain the relevant change in clear, concise language.
- Return only the answer, without creating citations.
"""

    answer = generate_answer(prompt)

    citations = [
        {
            "section": change["section"],
            "old_version": change["old_version"],
            "new_version": change["new_version"],
        }
        for change in changes
    ]

    return {
        "policy_name": policy_name,
        "answer": answer,
        "citations": citations,
    }