import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

DESKTOP = os.path.expanduser("~/Desktop")

def read_file(filename: str) -> str:
    path = os.path.join(DESKTOP, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_markdown(filename: str, content: str) -> str:
    path = os.path.join(DESKTOP, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} characters to {path}"

read_file_tool = {
    "type": "function",
    "name": "read_file",
    "description": "Reads the full text content of a file located on the Desktop.",
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "The file name, e.g. 'No Lines.txt'"}
        },
        "required": ["filename"]
    }
}

write_markdown_tool = {
    "type": "function",
    "name": "write_markdown",
    "description": "Writes text content to a new markdown file on the Desktop.",
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "The output file name, e.g. 'Summary.md'"},
            "content": {"type": "string", "description": "The markdown content to write"}
        },
        "required": ["filename", "content"]
    }
}

available_functions = {
    "read_file": read_file,
    "write_markdown": write_markdown
}

tools = [read_file_tool, write_markdown_tool]

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Read the file 'No Lines.txt', summarize it in 3-4 sentences, "
          "and write that summary to a new file called 'No Lines Summary.md'.",
    tools=tools
)

while any(step.type == "function_call" for step in interaction.steps):
    for step in interaction.steps:
        if step.type == "function_call":
            print(f"Model wants to call: {step.name} with {step.arguments}")
            fn = available_functions[step.name]
            result = fn(**step.arguments)
            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                previous_interaction_id=interaction.id,
                tools=tools,
                input=[{
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": result
                }]
            )

print(interaction.output_text)