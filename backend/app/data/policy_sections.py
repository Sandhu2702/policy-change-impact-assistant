import re


def extract_policy_sections(text: str) -> dict[str, str]:
    """Extract numbered policy sections and their content."""
    sections = {}
    current_heading = None
    current_content = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Match headings such as "1. Annual Leave Entitlement"
        match = re.match(r"^\d+\.\s+(.+)$", line)

        if match:
            if current_heading is not None:
                sections[current_heading] = " ".join(current_content)

            current_heading = match.group(1).strip()
            current_content = []
        elif current_heading is not None:
            current_content.append(line)

    if current_heading is not None:
        sections[current_heading] = " ".join(current_content)

    return sections