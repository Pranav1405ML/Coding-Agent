from agent.chat import send_message

history = []
print("Chat started. Type 'exit' to quit.\n")

try:
    while True:
        user_input = input("You: ")

        if user_input.strip() == "":
            print("(empty message, try again)")
            continue

        if user_input.lower() == "exit":
            break

        response_text, history = send_message(history, user_input)
        print(f"Gemini: {response_text}")

except KeyboardInterrupt:
    print("\n\nChat ended by user. Goodbye!")


# You: list the files in the agent folder, then read tools.py, write a explain.txt for this project

