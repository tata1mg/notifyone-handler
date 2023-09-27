import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger()


def log_combined_error(title, exception):
    request_params = {"exception": exception}
    logger.error(title, extra=request_params)
    combined_error = title + " " + exception
    logger.info(combined_error)


def log_combined_exception(title, exception):
    error = "Exception type {} , exception {}".format(type(exception), exception)
    log_combined_error(title, error)


def get_value_by_priority(
    dictionary: Dict[str, Any], keys_to_try: List[str], default: Optional[Any] = None
) -> Any:
    """
    Fetch key's value from a dict from a list of given keys.
    If multiple keys are present, then first one present is returned
    """

    for key in keys_to_try:
        if dictionary.get(key):
            return dictionary[key]
    return default


def json_dumps(json_obj: dict):
    return json.dumps(json_obj)


def json_loads(json_str: str):
    return json.loads(json_str)
