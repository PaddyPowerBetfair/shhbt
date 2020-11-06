from typing import List, Optional


def extract_additions(text: str) -> List[Optional[str]]:
    """
    extract_additions takes a diff content and returns a list of only the additions of text, which are the only
    things we want this command to parse.
    If no additions are found, it returns False, None. Otherwise, returns True, List.
    """
    # take all addiions from diff but drop newlines
    return [line for line in text.split("\n") if line.startswith("+") and len(line) > 1]
