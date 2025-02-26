### Helper function to parse values
import ast


def parse_value(value: str):
    """
    Attempts to convert a string to an appropriate type: bool, int, float, str, or list.
    """
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    try:
        parsed_value = ast.literal_eval(value)
        if isinstance(parsed_value, list):
            return [parse_value(str(element)) for element in parsed_value]
    except (ValueError, SyntaxError):
        pass

    return value