import json
import re
from typing import Dict, List


def extract_secrets_json(input_str: str) -> Dict[str, List[str]]:
    """
    Extracts the first valid JSON object with structure {"secrets": [string, ...]} from the input.
    Returns {"secrets": []} if extraction or validation fails.
    """
    # Match candidate JSON objects (non-greedy)
    candidate_jsons = re.findall(r'\{.*?\}', input_str, re.DOTALL)

    for candidate in candidate_jsons:
        try:
            obj = json.loads(candidate)
            if (
                isinstance(obj, dict)
                and "secrets" in obj
                and isinstance(obj["secrets"], list)
                and all(isinstance(s, str) for s in obj["secrets"])
            ):
                return obj
        except json.JSONDecodeError:
            continue

    # Fallback if no valid match found
    return {"secrets": []}
