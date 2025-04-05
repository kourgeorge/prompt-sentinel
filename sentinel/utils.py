import json


def parse_json_output(input_str):
    """
    Parses a string containing JSON data wrapped in Markdown code fences (```json ... ```),
    and returns the corresponding Python object.

    Args:
        input_str (str): The input string containing JSON data.

    Returns:
        object: The Python object parsed from the JSON string.

    Raises:
        json.JSONDecodeError: If the JSON parsing fails.
    """
    # Remove Markdown code fences if present
    stripped = input_str.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        # Split into lines and remove the first and last lines (the fences)
        lines = stripped.splitlines()
        # Remove the starting fence if it starts with ```json or ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove the ending fence
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        json_str = "\n".join(lines)
    else:
        json_str = input_str

    # Parse and return the JSON data
    return json.loads(json_str)
