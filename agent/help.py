from google import genai
from google.genai import types
from agent.tool_declarations import all_tools
from dotenv import load_dotenv
from agent.tools import TOOL_REGISTRY

load_dotenv()
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="can u list files in agent folder",
    config=types.GenerateContentConfig(
        tools=[all_tools]
    )
)

function_call = response.candidates[0].content.parts[0].function_call

if function_call:
    print("Tool requested:", function_call.name)
    print("Arguments given:", function_call.args)
    result = TOOL_REGISTRY[function_call.name]["function"](**function_call.args)
    print(result)

else:
    print(response.text)

