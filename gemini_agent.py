import os
import json

from dotenv import load_dotenv
from google import genai

from tools import calculator, get_current_time
from pdf_tool import search_pdf
from memory import ConversationMemory


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


memory = ConversationMemory()


# -----------------------------
# Calculator tool
# -----------------------------

calculator_tool = {
    "type": "function",
    "name": "calculator",
    "description": "Calculate a mathematical expression.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to calculate."
            }
        },
        "required": ["expression"]
    }
}


# -----------------------------
# Time tool
# -----------------------------

time_tool = {
    "type": "function",
    "name": "get_current_time",
    "description": "Get the current local time.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}


# -----------------------------
# PDF tool
# -----------------------------

pdf_tool = {
    "type": "function",
    "name": "search_pdf",
    "description": "Search the DBMS PDF for information relevant to the user's question.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Question to search for in the PDF."
            }
        },
        "required": ["question"]
    }
}


print("Gemini AI Agent")
print("Type 'exit' to stop.")
print()


while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break


    # Save user message
    memory.add_message(
        "user",
        user_input
    )


    # Build conversation history
    conversation = ""

    for message in memory.get_history():

        conversation += (
            message["role"]
            + ": "
            + message["message"]
            + "\n"
        )


    # Ask Gemini
    interaction = client.interactions.create(
        model="gemini-3.8-flash",

        input=f"""
You are a helpful AI agent.

Conversation history:
{conversation}

Answer the user's latest question.

You can use these tools when necessary:
- calculator
- get_current_time
- search_pdf

Use the PDF tool when the user asks about information
that may be contained in the DBMS notes.

Be concise and helpful.
""",

        tools=[
            calculator_tool,
            time_tool,
            pdf_tool
        ]
    )


    # Check whether Gemini requested a tool
    tool_used = False

    for step in interaction.steps:

        if step.type == "function_call":

            tool_used = True

            print("Gemini selected:", step.name)


            if step.name == "calculator":

                result = calculator(
                    **step.arguments
                )


            elif step.name == "get_current_time":

                result = get_current_time()


            elif step.name == "search_pdf":

                result = search_pdf(
                    **step.arguments
                )


            else:

                result = "Unknown tool"


            print("Tool result:", result)


            # Send result back to Gemini
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


            answer = final_interaction.output_text

            print("Agent:", answer)


            memory.add_message(
                "assistant",
                answer
            )

            break


    # No tool was required
    if not tool_used:

        answer = interaction.output_text

        print("Agent:", answer)

        memory.add_message(
            "assistant",
            answer
        )


    print()