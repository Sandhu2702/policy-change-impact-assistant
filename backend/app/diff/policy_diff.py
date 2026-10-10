import re


def normalize_rule(rule: str) -> str:
    """Normalize a rule for comparison."""
    return " ".join(rule.split()).strip()


def compare_rules(
    old_rules: list[str],
    new_rules: list[str],
) -> list[dict[str, str]]:
    """Detect added, removed, and modified policy rules."""
    old_normalized = [normalize_rule(rule) for rule in old_rules]
    new_normalized = [normalize_rule(rule) for rule in new_rules]

    changes = []
    matched_old = set()
    matched_new = set()

    # Step 1: Match identical rules first.
    for old_index, old_rule in enumerate(old_normalized):
        for new_index, new_rule in enumerate(new_normalized):
            if new_index not in matched_new and old_rule == new_rule:
                matched_old.add(old_index)
                matched_new.add(new_index)
                break

    # Step 2: Pair remaining old and new rules as modifications.
    remaining_old = [
        (index, rule)
        for index, rule in enumerate(old_normalized)
        if index not in matched_old
    ]
    remaining_new = [
        (index, rule)
        for index, rule in enumerate(new_normalized)
        if index not in matched_new
    ]

    pair_count = min(len(remaining_old), len(remaining_new))

    for index in range(pair_count):
        _, old_rule = remaining_old[index]
        _, new_rule = remaining_new[index]

        changes.append({
            "change_type": "MODIFY",
            "old_text": old_rule,
            "new_text": new_rule,
        })

    # Step 3: Any unmatched old rules were removed.
    for _, old_rule in remaining_old[pair_count:]:
        changes.append({
            "change_type": "REMOVE",
            "old_text": old_rule,
            "new_text": "",
        })

    # Step 4: Any unmatched new rules were added.
    for _, new_rule in remaining_new[pair_count:]:
        changes.append({
            "change_type": "ADD",
            "old_text": "",
            "new_text": new_rule,
        })

    return changes


def compare_policy_sections(
    old_sections: dict[str, str],
    new_sections: dict[str, str],
) -> list[dict[str, str]]:
    """Compare policy sections by heading."""
    changes = []

    all_headings = sorted(set(old_sections) | set(new_sections))

    for heading in all_headings:
        old_text = old_sections.get(heading)
        new_text = new_sections.get(heading)

        if old_text is None:
            changes.append({
                "change_type": "ADD",
                "section": heading,
                "old_text": "",
                "new_text": new_text or "",
            })
        elif new_text is None:
            changes.append({
                "change_type": "REMOVE",
                "section": heading,
                "old_text": old_text,
                "new_text": "",
            })
        elif old_text != new_text:
            changes.append({
                "change_type": "MODIFY",
                "section": heading,
                "old_text": old_text,
                "new_text": new_text,
            })

    return changes