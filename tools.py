from datetime import datetime


def calculator(expression):
    try:
        allowed = "0123456789+-*/(). %"

        if not all(char in allowed for char in expression):
            return "Invalid expression"

        return eval(expression)

    except Exception:
        return "Invalid calculation"


def get_current_time():
    return datetime.now().strftime("%I:%M %p")