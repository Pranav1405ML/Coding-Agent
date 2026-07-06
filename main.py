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


if __name__ == "__main__":
    run()


# (venv) PS D:\Projects\Coding Agent> pip install -e .
# Obtaining file:///D:/Projects/Coding%20Agent
#   Installing build dependencies ... done
#   Checking if build backend supports build_editable ... done
#   Getting requirements to build editable ... done
#   Preparing editable metadata (pyproject.toml) ... done
# Requirement already satisfied: google-genai>=1.0.0 in .\venv\Lib\site-packages (from agent-cody==0.1.0) (2.8.0)
# Requirement already satisfied: anyio<5.0.0,>=4.8.0 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (4.14.0)
# Requirement already satisfied: google-auth<3.0.0,>=2.48.1 in .\venv\Lib\site-packages (from google-auth[requests]<3.0.0,>=2.48.1->google-genai>=1.0.0->agent-cody==0.1.0) (2.55.0)
# Requirement already satisfied: httpx<1.0.0,>=0.28.1 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (0.28.1)
# Requirement already satisfied: pydantic<3.0.0,>=2.9.0 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (2.13.4)
# Requirement already satisfied: requests<3.0.0,>=2.28.1 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (2.34.2)
# Requirement already satisfied: tenacity<9.2.0,>=8.2.3 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (9.1.4)
# Requirement already satisfied: websockets<17.0,>=13.0.0 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (16.0)
# Requirement already satisfied: typing-extensions<5.0.0,>=4.14.0 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (4.15.0)
# Requirement already satisfied: distro<2,>=1.7.0 in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (1.9.0)
# Requirement already satisfied: sniffio in .\venv\Lib\site-packages (from google-genai>=1.0.0->agent-cody==0.1.0) (1.3.1)
# Requirement already satisfied: idna>=2.8 in .\venv\Lib\site-packages (from anyio<5.0.0,>=4.8.0->google-genai>=1.0.0->agent-cody==0.1.0) (3.18)
# Requirement already satisfied: pyasn1-modules>=0.2.1 in .\venv\Lib\site-packages (fr
# om google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=1.0.0->agent-cody==0.1.0) (0.4.2)
# Requirement already satisfied: cryptography>=38.0.3 in .\venv\Lib\site-packages (fro
# m google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=1.0.0->agent-cody==0.1.0) (49.0.0)
# Requirement already satisfied: certifi in .\venv\Lib\site-packages (from httpx<1.0.0,>=0.28.1->google-genai>=1.0.0->agent-cody==0.1.0) (2026.6.17)
# Requirement already satisfied: httpcore==1.* in .\venv\Lib\site-packages (from httpx<1.0.0,>=0.28.1->google-genai>=1.0.0->agent-cody==0.1.0) (1.0.9)
# Requirement already satisfied: h11>=0.16 in .\venv\Lib\site-packages (from httpcore==1.*->httpx<1.0.0,>=0.28.1->google-genai>=1.0.0->agent-cody==0.1.0) (0.16.0)
# Requirement already satisfied: annotated-types>=0.6.0 in .\venv\Lib\site-packages (from pydantic<3.0.0,>=2.9.0->google-genai>=1.0.0->agent-cody==0.1.0) (0.7.0)
# Requirement already satisfied: pydantic-core==2.46.4 in .\venv\Lib\site-packages (from pydantic<3.0.0,>=2.9.0->google-genai>=1.0.0->agent-cody==0.1.0) (2.46.4)
# Requirement already satisfied: typing-inspection>=0.4.2 in .\venv\Lib\site-packages (from pydantic<3.0.0,>=2.9.0->google-genai>=1.0.0->agent-cody==0.1.0) (0.4.2)
# Requirement already satisfied: charset_normalizer<4,>=2 in .\venv\Lib\site-packages (from requests<3.0.0,>=2.28.1->google-genai>=1.0.0->agent-cody==0.1.0) (3.4.7)
# Requirement already satisfied: urllib3<3,>=1.26 in .\venv\Lib\site-packages (from requests<3.0.0,>=2.28.1->google-genai>=1.0.0->agent-cody==0.1.0) (2.7.0)
# Requirement already satisfied: cffi>=2.0.0 in .\venv\Lib\site-packages (from cryptog
# raphy>=38.0.3->google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=1.0.0->agent-cody==0.1.0) (2.0.0)
# Requirement already satisfied: pycparser in .\venv\Lib\site-packages (from cffi>=2.0
# .0->cryptography>=38.0.3->google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=1.0.0->agent-cody==0.1.0) (3.0)
# Requirement already satisfied: pyasn1<0.7.0,>=0.6.1 in .\venv\Lib\site-packages (fro
# m pyasn1-modules>=0.2.1->google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=1.0.0->agent-cody==0.1.0) (0.6.3)
# Building wheels for collected packages: agent-cody
#   Building editable for agent-cody (pyproject.toml) ... done
#   Created wheel for agent-cody: filename=agent_cody-0.1.0-0.editable-py3-none-any.whl size=3076 sha256=2c28f4f4be8aa44b582f4bfc9be0f27762f4af4ad02cf153c9de1c299bf42fdd
#   Stored in directory: C:\Users\ganes\AppData\Local\Temp\pip-ephem-wheel-cache-eowdps8l\wheels\d6\69\0f\317e64504d48b73855c7e5ed941bd64097d77cddd91afe5375
# Successfully built agent-cody
# Installing collected packages: agent-cody
# Successfully installed agent-cody-0.1.0