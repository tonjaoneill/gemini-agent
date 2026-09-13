import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

ARTICLES_DIR = os.path.expanduser("~/Desktop/Articles")
CATALOG_PATH = os.path.join(ARTICLES_DIR, "catalog.md")

@tool
def list_files() -> list:
    """Lists all .txt article filenames in the Articles folder."""
    return [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".txt")]

@tool
def read_file(filename: str) -> str:
    """Reads the full text content of a .txt file in the Articles folder."""
    path = os.path.join(ARTICLES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@tool
def read_catalog() -> str:
    """Reads the existing catalog.md file. Returns empty string if it doesn't exist yet."""
    if not os.path.exists(CATALOG_PATH):
        return ""
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return f.read()

@tool
def append_to_catalog(entry: str) -> str:
    """Appends a new markdown entry to catalog.md. Creates the file if needed."""
    with open(CATALOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n\n")
    return f"Appended entry to {CATALOG_PATH}"

tools = [list_files, read_file, read_catalog, append_to_catalog]

agent = create_agent("google_genai:gemini-3.6-flash", tools=tools)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "Check the existing catalog to see what's already summarized. "
            "List available .txt files. For any file NOT already in the catalog, "
            "read it, write a 3-4 sentence summary, and append it to the catalog "
            "formatted as:\n## <filename>\n<summary>\n\n"
            "Skip files already in the catalog. Tell me what you processed and skipped."
        )
    }]
})

final_message = result["messages"][-1]
if isinstance(final_message.content, str):
    print(final_message.content)
else:
    for block in final_message.content:
        if isinstance(block, dict) and block.get("type") == "text":
            print(block["text"])
            