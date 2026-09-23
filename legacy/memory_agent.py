import os

from dotenv import load_dotenv
from google import genai

from memory import ConversationMemory


# Load API key
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Create memory
memory = ConversationMemory()


print("AI Agent with Memory")
print("Type 'exit' to stop.")
print()


while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break


    # Save user's message
    memory.add_message(
        "user",
        user_input
    )


    # Get conversation history
    history = memory.get_history()


    # Convert history into text
    conversation = ""

    for message in history:

        conversation += (
            message["role"]
            + ": "
            + message["message"]
            + "\n"
        )


    # Send conversation to Gemini
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=f"""
You are a helpful AI assistant.

Here is the conversation so far:

{conversation}

Answer the user's latest question while
remembering the previous conversation.
"""
    )


    answer = interaction.output_text


    # Save Gemini's response
    memory.add_message(
        "assistant",
        answer
    )


    print("Agent:", answer)
    print()