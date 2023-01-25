import logging
import re

def create_logger(name: str, log_level = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def empty_str_to_none(str) -> None:
    if str is None:
        return str
    elif str == '':
        return None
    else:
        return str

def setBudget(min_budget, max_budget):
    if max_budget is None and min_budget is None:
        return None
    if max_budget is None and min_budget is not None:
        return f'{min_budget}$'
    if max_budget is not None and min_budget is None:
        return f'{max_budget}$'

    return f'{min_budget}$ - {max_budget}$'

def getPhoneNumberFromDescription(description: str):
    phone_numbers = re.search(r'((\+)?\b(8|38)?(0[\d]{2}))([\d-]{5,8})([\d]{2})', description)
    if phone_numbers:
        return phone_numbers.group(0)

def getEmailFromDescription(description: str):
    email = re.findall(r'\b([a-z0-9._-]+@[a-z0-9.-]+)\b', description)
    email = '/'.join(list(set(email)))
    return email