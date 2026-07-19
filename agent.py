import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from tools import web_search, calculator, file_reader
from schemas import ResearchAnswer

load_dotenv()


SYSTEM_PROMPT = """You are ResearchBot, an AI Research Assistant.

ROLE:
You help users research topics by finding accurate, up-to-date information,
performing calculations when needed, and reading documents when provided.

GOAL:
Give the user a clear, well-organized, and accurate answer to their research
question, using tools whenever your own knowledge might be outdated or
insufficient.

INSTRUCTIONS:
1. Think step by step before answering. Decide if you need a tool or if you
   can answer directly from what you already know.
2. CRITICAL RULE: You do not know what "today's date" is, and your training
   data has a cutoff in the past. Any question mentioning a year, "latest",
   "recent", "current", or "today" is a signal that your own knowledge may
   be outdated. In ALL such cases, you MUST call web_search first before
   answering. NEVER say a year is "in the future" or that you "cannot predict
   future events", you have a web_search tool specifically to handle this.
   Refusing to search is a failure, not a safe response.
3. Use the calculator tool for any math, percentages, or numeric comparisons.
   Never do math in your head, always call the calculator.
4. Use the file_reader tool only when the user refers to an uploaded
   document.
5. If one search isn't enough to fully answer the question, search again
   with a refined query rather than guessing.
6. When citing sources, always extract the actual URL or publication name
   from tool results. Never write the literal tool name (e.g. "web_search",
   "calculator") as a source.
7. If a question is ambiguous or could mean several things, briefly state
   the assumption you're making rather than silently guessing.
8. Keep the final answer clear and organized, use bullet points or short
   sections when appropriate.

CONSTRAINTS:
- Never make up facts, dates, statistics, or sources. If you don't know and
  can't find it, say so honestly.
- Never call a tool unless it's actually needed for the task.
- Do not repeat the same tool call with the same input twice.
- Keep responses focused, no unnecessary filler text.
"""

# Change model here, or set AGENT_MODEL env var.
# Use gemini-3.1-flash-lite for development/testing (higher free-tier quota),
# switch to gemini-2.5-flash for the final demo recording.
MODEL_NAME = os.getenv("AGENT_MODEL", "gemini-3.1-flash-lite")

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0,
)

checkpointer = InMemorySaver()

# NOTE: response_format is intentionally NOT passed to create_agent here.
# Combining tools + response_format in LangChain 1.0 causes the agent to
# re-enter its reasoning loop (a known framework issue with Gemini models,
# not fully reliable even on Gemini 3), sometimes duplicating tool calls.
# Instead, the ReAct loop runs first (tools only), then a separate,
# tool-free call formats the final answer into the schema. See README
# "Known Limitations" for details.
agent = create_agent(
    model=llm,
    tools=[web_search, calculator, file_reader],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)

# Separate formatter: no tools bound, so it cannot trigger a new search/loop.
structured_llm = llm.with_structured_output(ResearchAnswer)


if __name__ == "__main__":
    query = "What are the latest breakthroughs in quantum computing in 2026?"

    # Step 1: run the normal ReAct loop (reasoning + tools)
    result = agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config={"configurable": {"thread_id": "test-thread"}},
    )

    for msg in result["messages"]:
        print(f"\n--- {msg.__class__.__name__} ---")
        print(msg.text if msg.content else msg.tool_calls)

    final_answer_text = result["messages"][-1].text
    print("\n\nFINAL ANSWER (raw):\n", final_answer_text)

    # Step 2: separate, tool-free call to format into the Pydantic schema
    structured = structured_llm.invoke(
        f"Convert this research answer into the required structured format:\n\n{final_answer_text}"
    )
    print("\n\nSTRUCTURED OUTPUT:\n", structured)