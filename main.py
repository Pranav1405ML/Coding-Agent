import os
from agent.chat import send_message
from agent.config import set_project_root


message, success = set_project_root(os.getcwd())
if not success:
    print(message)

else:
    history = []
    print(message)
    print(f"Workspace: {os.getcwd()}")
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


