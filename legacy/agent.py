import os
import json

from dotenv import load_dotenv
from google import genai

from tools import calculator, get_current_time


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Calculator tool
calculator_tool = {
    "type": "function",
    "name": "calculator",
    "description": "Calculate a mathematical expression.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to calculate."
            }
        },
        "required": ["expression"]
    }
}


# Current time tool
time_tool = {
    "type": "function",
    "name": "get_current_time",
    "description": "Get the current local time.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}


# Ask the user
user_input = input("You: ")


# Send question to Gemini
interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=user_input,
    tools=[
        calculator_tool,
        time_tool
    ]
)


# Check Gemini's response
for step in interaction.steps:

    if step.type == "function_call":

        print("Gemini is using a tool...")

        if step.name == "calculator":
            result = calculator(**step.arguments)

        elif step.name == "get_current_time":
            result = get_current_time()

        else:
            result = "Unknown tool"

        # Send tool result back to Gemini
        final_interaction = client.interactions.create(
            model="gemini-3.8-flash",
            previous_interaction_id=interaction.id,
            input=[
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps(result)
                        }
                    ]
                }
            ]
        )

        print("Agent:", final_interaction.output_text)

        break

else:
    print("Agent:", interaction.output_text)