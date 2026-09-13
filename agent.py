import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

ARTICLES_DIR = os.path.expanduser("~/Desktop/Articles")
CATALOG_PATH = os.path.join(ARTICLES_DIR, "catalog.md")

def list_files() -> list:
    """Lists all .txt article filenames in the Articles folder."""
    return [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".txt")]

def read_file(filename: str) -> str:
    """Reads the full text content of a .txt file in the Articles folder."""
    path = os.path.join(ARTICLES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_catalog() -> str:
    """Reads the existing catalog.md file. Returns empty string if it doesn't exist yet."""
    if not os.path.exists(CATALOG_PATH):
        return ""
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return f.read()

def append_to_catalog(entry: str) -> str:
    """Appends a new entry (filename + summary) to catalog.md. Creates the file if needed."""
    with open(CATALOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n\n")
    return f"Appended entry to {CATALOG_PATH}"

list_files_tool = {
    "type": "function",
    "name": "list_files",
    "description": "Lists all .txt article filenames currently in the Articles folder.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

read_file_tool = {
    "type": "function",
    "name": "read_file",
    "description": "Reads the full text content of a specific .txt file in the Articles folder.",
    "parameters": {
        "type": "object",
        "properties": {"filename": {"type": "string", "description": "e.g. 'No Lines.txt'"}},
        "required": ["filename"]
    }
}

read_catalog_tool = {
    "type": "function",
    "name": "read_catalog",
    "description": "Reads the existing catalog.md to see which articles have already been summarized.",
    "parameters": {"type": "object", "properties": {}, "required": []}
}

append_to_catalog_tool = {
    "type": "function",
    "name": "append_to_catalog",
    "description": "Appends a new markdown entry (## filename, followed by a summary) to catalog.md.",
    "parameters": {
        "type": "object",
        "properties": {"entry": {"type": "string", "description": "Markdown-formatted entry to append"}},
        "required": ["entry"]
    }
}

available_functions = {
    "list_files": list_files,
    "read_file": read_file,
    "read_catalog": read_catalog,
    "append_to_catalog": append_to_catalog
}

tools = [list_files_tool, read_file_tool, read_catalog_tool, append_to_catalog_tool]

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input=(
        "You maintain a catalog of summarized articles. First, check the existing catalog "
        "to see what's already been summarized. Then list the available .txt files. "
        "For any file NOT already in the catalog, read it, write a 3-4 sentence summary, "
        "and append a new entry to the catalog formatted as:\n"
        "## <filename>\n<summary>\n\n"
        "Skip any file already in the catalog. Tell me at the end which files you processed "
        "and which you skipped."
    ),
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
                    "result": [{"type": "text", "text": json.dumps(result)}]
                }]
            )

print(interaction.output_text)