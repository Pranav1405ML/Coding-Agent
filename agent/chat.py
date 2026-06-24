from dotenv import load_dotenv
from google import genai
from agent.tool_declarations import all_tools
from agent.tools import TOOL_REGISTRY
from google.genai import types
import os

# Load the .env file so Python can access your API key
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def send_message(history: list, user_message: str) -> tuple:
    temp_history = history + [{"role": "user", "parts": [{"text": user_message}]}]


    while True:
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=temp_history,
                config=types.GenerateContentConfig(
                    tools=[all_tools]
                )
            )
        # You're capturing that error object into the variable e, so you can inspect it, log it, or show it to the user — instead of just knowing "something broke" with zero detail.
        except Exception as e:
            return f"[Error: Could not get a response. {e}]", history

        function_call = response.candidates[0].content.parts[0].function_call

        if function_call:
            temp_history.append(response.candidates[0].content)
            try:
                result = TOOL_REGISTRY[function_call.name]["function"](**function_call.args)  # KeyError will be caught in exception as e
            except KeyError as e:
                return f"[Error: Key does not exist in Tool Registry. {e}]", history
            except TypeError as e:
                return f"[Error: Invalid number of parameters. {e}]", history
            except Exception as e:
                return f"[Error: Something went wrong, {e}]", history

            temp_history.append({"role": "function", "parts": [{"function_response": {"name": function_call.name, "response": {"result": result}}}]})

        else:
            temp_history.append({"role": "model", "parts": [{"text": response.text}]})
            history = temp_history
            return response.text, history



