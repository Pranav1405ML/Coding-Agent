import os
import sys
from agent.chat import send_message
from agent.config import set_project_root

def run():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set. Please set it before running the agent.")
        sys.exit(1)

    print("Success: GEMINI_API_KEY environment variable has been set.")

    message, success = set_project_root(os.getcwd())
    if not success:
        print(message)
        sys.exit(1)

    history = []
    print(message)
    print(f"Workspace: {os.getcwd()}")
    print("Chat started. Type 'exit' to quit.\n")

    try:
        while True:
            print()
            user_input = input("\033[96mYou: \033[0m")

            if user_input.strip() == "":
                print("(empty message, try again)")
                continue

            if user_input.lower() == "exit":
                break

            response_text, history = send_message(history, user_input)
            print()
            print(f"\033[96mAgent Cody: \033[0m{response_text}")

    except KeyboardInterrupt:
        print("\n\nChat ended by user. Goodbye!")


if __name__ == "__main__":
    run()
