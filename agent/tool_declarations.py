from google.genai import types
from agent.tools import TOOL_REGISTRY

tool_declaration_list = []

for tool in TOOL_REGISTRY.values():
    property_dict = {}
    for param, info in tool["parameters"].items():
        property_dict[param] = {"type" : info.split("-", 1)[0].strip(), "description" : info.split("-", 1)[1].strip()}

    tool_declaration = types.FunctionDeclaration(
        name=tool["name"],
        description=tool["description"],
        parameters={
            "type": "object",
            "properties": property_dict,
            "required": list(property_dict.keys())
        }
    )

    tool_declaration_list.append(tool_declaration)

all_tools = types.Tool(
    function_declarations=tool_declaration_list
)



