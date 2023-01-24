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
    phone_numbers = re.findall(r'[0-9]{10}', description)
    phone_numbers = '/'.join(list(set(phone_numbers)))
    return phone_numbers

def getEmailFromDescription(description: str):
    email = re.findall(r'\b([a-z0-9._-]+@[a-z0-9.-]+)\b', description)
    email = '/'.join(list(set(email)))
    return email