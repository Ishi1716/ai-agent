from tools import calculator, get_current_time
from planner import decide_tool
from pdf_tool import search_pdf
from memory import ConversationMemory


# Create conversation memory
memory = ConversationMemory()


print("AI Agent with Tools + Memory")
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

    # Decide which tool to use
    tool = decide_tool(user_input)

    # Store result
    result = ""

    # Calculator
    if tool == "calculator":

        expression = input("Enter calculation: ")

        result = calculator(expression)

        print("Tool used: Calculator")
        print("Result:", result)

    # Current time
    elif tool == "get_current_time":

        result = get_current_time()

        print("Tool used: Current Time")
        print("Result:", result)

    # PDF / RAG
    elif tool == "pdf":

        result = search_pdf(user_input)

        print("Tool used: PDF/RAG")
        print()
        print("Relevant information:")
        print(result)

    # No tool
    else:

        print("Tool used: None")

        print("Agent: I remember this conversation.")

        print()
        print("Conversation so far:")

        for message in memory.get_history():

            print(
                message["role"],
                ":",
                message["message"]
            )

        result = "Conversation history displayed."

    # Save agent response
    memory.add_message(
        "assistant",
        result
    )

    print()