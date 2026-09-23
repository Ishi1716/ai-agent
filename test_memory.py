from memory import ConversationMemory


memory = ConversationMemory()


memory.add_message(
    "user",
    "My name is Ishita."
)

memory.add_message(
    "assistant",
    "Nice to meet you, Ishita!"
)

memory.add_message(
    "user",
    "I am studying BTech IT."
)


print("Conversation History:")
print()

for message in memory.get_history():

    print(
        message["role"],
        ":",
        message["message"]
    )


