import logging
import re
from typing import Optional


def create_logger(name: str, log_level=logging.DEBUG) -> logging.Logger:
    """
    Creates a logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def empty_str_to_none(s: Optional[str]) -> Optional[str]:
    """
    Converts an empty string to Null
    """
    if s is None:
        return s
    elif s == '':
        return None
    else:
        return s


def set_budget(min_budget: Optional[str], max_budget: Optional[str]) -> str:
    """
    Sets a price format
    """
    if max_budget is None and min_budget is None:
        return None
    if max_budget is None and min_budget is not None:
        return f'{min_budget}$'
    if max_budget is not None and min_budget is None:
        return f'{max_budget}$'

    return f'{min_budget}$ - {max_budget}$'


def get_phone_number(s: str) -> Optional[str]:
    """
    Gets a phone number from string
    """
    phone_numbers = re.search(r'((\+)?\b(8|38)?([\d]{3}))([\d-]{5,8})([\d]{2})', s)
    if phone_numbers:
        return phone_numbers.group(0)


def get_email(s: str) -> str:
    """
    Gets an email from string
    """
    email = re.findall(r'\b([a-z0-9._-]+@[a-z0-9.-]+)\b', s)
    email = '/'.join(list(set(email)))
    return email
