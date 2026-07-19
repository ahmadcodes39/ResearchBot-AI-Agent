from langchain_community.tools import DuckDuckGoSearchResults
from langchain.tools import tool
from pypdf import PdfReader

# Tool 1: Web Search 
search_tool = DuckDuckGoSearchResults(output_format="list")

@tool
def web_search(query: str) -> str:
    """Search the web for current information, news, or facts you don't know confidently.
    Returns a list of results including title, link, and snippet for each source.
    Use this when the question involves recent events, current data, or unfamiliar topics."""
    try:
        results = search_tool.invoke(query)
        # Format results so the LLM can see and cite actual source titles/links
        formatted = []
        for r in results:
            title = r.get("title", "Unknown title")
            link = r.get("link", "No link available")
            snippet = r.get("snippet", "")
            formatted.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")
        return "\n\n".join(formatted) if formatted else "No results found."
    except Exception as e:
        return f"Web search failed: {str(e)}. Try rephrasing the query or proceed without it."
    
# Tool 2: Calculator
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Use this for any math, percentages,
    or numeric comparisons instead of calculating in your head.
    Example input: '(1700 - 1200) / 1200 * 100'"""
    try:
        # Only allow safe characters to avoid arbitrary code execution
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Invalid expression: only numbers and + - * / ( ) are allowed."
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Calculation failed: {str(e)}. Please check the expression format."

# Tool 3: File Reader (PDF or TXT)
@tool
def file_reader(file_path: str) -> str:
    """Read the text content of a PDF or TXT file the user has provided.
    Input should be the full file path. Use this only when the user
    references an uploaded document."""
    try:
        if file_path.lower().endswith(".pdf"):
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text[:5000] if text else "No readable text found in this PDF."
        elif file_path.lower().endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()[:5000]
        else:
            return "Unsupported file type. Only .pdf and .txt are supported."
    except FileNotFoundError:
        return f"File not found at path: {file_path}"
    except Exception as e:
        return f"File reading failed: {str(e)}"