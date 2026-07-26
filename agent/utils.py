import json
import logging

logger = logging.getLogger(__name__)


def safe_json_loads(data):
    """
    Safely parse JSON string.
    Returns original data if parsing fails.
    """
    if data is None:
        return None

    if isinstance(data, (dict, list)):
        return data

    try:
        return json.loads(data)
    except Exception:
        return data


def normalize_text(text):
    """
    Normalize user input.
    """
    if text is None:
        return ""

    return " ".join(str(text).strip().split())


def extract_limit(text, default=10):
    """
    Extract numeric limit from user query.

    Example:
        top 5 assets -> 5
        show 20 commodities -> 20
    """
    import re

    match = re.search(r"\b(\d+)\b", text)

    if match:
        return int(match.group(1))

    return default


def success_response(data):
    """
    Standard success response.
    """
    return {
        "success": True,
        "data": data
    }


def error_response(message):
    """
    Standard error response.
    """
    return {
        "success": False,
        "error": message
    }


def log_exception(ex):
    """
    Log exceptions.
    """
    logger.exception(ex)


def truncate_text(text, length=60):
    """
    Truncate long text.
    """
    if not text:
        return ""

    if len(text) <= length:
        return text

    return text[:length] + "..."


def format_chat_title(message):
    """
    Generate chat title from first user message.
    """
    message = normalize_text(message)

    if len(message) <= 50:
        return message

    return message[:50] + "..."


def is_json(text):
    """
    Check if string is valid JSON.
    """
    if not isinstance(text, str):
        return False

    try:
        json.loads(text)
        return True
    except Exception:
        return False


def pretty_json(data):
    """
    Pretty-print JSON.
    """
    try:
        return json.dumps(data, indent=4, ensure_ascii=False)
    except Exception:
        return str(data)


def chunk_list(data, chunk_size=100):
    """
    Split list into chunks.
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def flatten_dict(dictionary, parent_key="", separator="."):
    """
    Flatten nested dictionary.

    Example:
    {
        "a": {
            "b": 1
        }
    }

    becomes

    {
        "a.b": 1
    }
    """
    items = []

    for key, value in dictionary.items():

        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(
                flatten_dict(value, new_key, separator).items()
            )
        else:
            items.append((new_key, value))

    return dict(items)


def remove_empty_values(data):
    """
    Remove None and empty strings from dictionary.
    """
    if not isinstance(data, dict):
        return data

    return {
        key: value
        for key, value in data.items()
        if value not in [None, "", [], {}]
    }


def safe_get(data, *keys, default=None):
    """
    Safely get nested dictionary values.

    Example:
        safe_get(obj, "data", "result", "name")
    """
    current = data

    for key in keys:

        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def unique_list(data):
    """
    Remove duplicates while preserving order.
    """
    seen = set()

    result = []

    for item in data:

        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def validate_user_message(message):
    """
    Validate incoming user message.
    """
    message = normalize_text(message)

    if not message:
        return False, "Message cannot be empty."

    if len(message) > 5000:
        return False, "Message is too long."

    return True, message