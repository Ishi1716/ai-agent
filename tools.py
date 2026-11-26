
from datetime import datetime
from zoneinfo import ZoneInfo


def calculator(expression):
    try:
        allowed = "0123456789+-*/(). %"

        if not all(char in allowed for char in expression):
            return "Invalid expression"

        return eval(expression)

    except Exception:
        return "Invalid calculation"


def get_current_time():
    india_time = datetime.now(ZoneInfo("Asia/Kolkata"))
    return india_time.strftime("%I:%M %p")
