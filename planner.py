def decide_tool(user_input):

    text = user_input.lower()

    # Calculator
    if any(symbol in text for symbol in ["+", "-", "*", "/", "%"]):
        return "calculator"

    # Time
    if "time" in text:
        return "get_current_time"

    # PDF / DBMS
    pdf_keywords = [
        "dbms",
        "database",
        "normalization",
        "normal form",
        "sql",
        "transaction",
        "primary key",
        "foreign key",
        "acid",
        "index",
        "relational"
    ]

    for keyword in pdf_keywords:

        if keyword in text:
            return "pdf"

    # No tool
    return "none"