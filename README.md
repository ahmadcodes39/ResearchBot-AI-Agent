# ResearchBot — AI Research Assistant Agent

An autonomous AI agent built with **LangChain** and **Google Gemini**, capable of
web search, calculation, and document reading, with memory, structured output, live
reasoning logs, and graceful error handling.

Built as part of the **Generative AI Internship — GAIRL, KICS, NCAI**
(Build an AI Agent).

---

## 1. Overview

ResearchBot is a **research assistant agent**, not a chatbot. Given a question, it
autonomously decides whether it can answer directly, or whether it needs to reason,
search the web, run a calculation, or read a local document, then loops through those
steps (ReAct: Reason → Act → Observe) until it has enough information to answer.

Unlike a plain chatbot (see [Section 8](#8-comparison-chatbot-vs-rag-vs-agent)), every
step of its reasoning is visible, its tools are fully customizable, and its final
answer is returned as validated structured data (JSON via Pydantic), not just prose.

---

## 2. Features (mapped to task requirements)

| # | Feature | Status |
|---|---|---|
| 1 | Framework: LangChain | ✅ |
| 2 | Use case: Research Assistant | ✅ |
| 3 | Role / Goal / Instructions / Constraints | ✅ |
| 4 | System prompt + agent instructions | ✅ |
| 5 | 3+ external tools (web search, calculator, file reader) | ✅ |
| 6 | Memory (multi-turn conversation) | ✅ |
| 7 | ReAct reasoning (Reason → Act → Observe) | ✅ |
| 8 | Task planning | ✅ (handled automatically inside the agent loop) |
| 9 | Tool calling / correct tool auto-selection | ✅ (verified individually + combined) |
| 10 | Structured output (Pydantic/JSON) | ✅ |
| 11 | Error handling + fallback responses | ✅ |
| 12 | Logging of agent execution + tool usage | ✅ (live timestamped logs) |
| 13 | Tested with multiple real-world scenarios/edge cases | ✅ (see `TEST_CASES.md`) |
| 14 | Compared against a basic chatbot and a RAG system | ✅ (see Section 8) |

---

## 3. Architecture

```
User Input
   |
   v
Agent (LLM + System Prompt)
   |
   v
Reasoning: "Do I need a tool, or can I answer directly?"
   |
   +--- No tool needed --------> Compose answer directly
   |
   +--- Tool needed
          |
          v
   Tool Selection (web_search / calculator / file_reader)
          |
          v
   Tool Execution --> Observation
          |
          v
   Reasoning again: "Do I have enough info now?"
          |
          +--- No --> loop back to Tool Selection (multi-step)
          |
          +--- Yes
                 |
                 v
        Structured Output (Pydantic: summary, key_findings, sources, confidence)
                 |
                 v
        Memory updated (LangGraph checkpointer, keyed by thread_id)
                 |
                 v
        Returned to user (formatted + logged live)
```

**Framework internals:** built on LangChain 1.0's `create_agent()`, which compiles this
loop as a LangGraph state graph under the hood. Memory is handled by a LangGraph
`InMemorySaver` checkpointer, keyed by a `thread_id` per conversation session.

---

## 4. Tech Stack

| Component | Choice | Why |
|---|---|---|
| Agent framework | LangChain 1.0 (`create_agent`) | Modern, official, replaces deprecated `AgentExecutor` |
| LLM | Google Gemini (`gemini-2.5-flash` / `gemini-3.1-flash-lite`) | Free tier available, good tool-calling support |
| Web search | DuckDuckGo (`langchain-community`) | No API key required |
| Memory | LangGraph `InMemorySaver` | Built into LangChain 1.0, no separate memory class needed |
| Structured output | Pydantic (`response_format=`) | Native LangChain 1.0 support, validated output |
| PDF/TXT reading | `pypdf` | Lightweight, no external service |

---

## 5. Project Structure

```
research_assistant/
├── .env.example        # Template for required API key
├── requirements.txt     # Exact working dependency versions
├── tools.py              # web_search, calculator, file_reader tool definitions
├── schemas.py            # Pydantic schema for structured output
├── agent.py              # System prompt + agent + LLM + checkpointer setup
├── main.py               # CLI chat loop (entry point) with live reasoning logs
├── sample.txt             # Sample file used to test file_reader tool
├── README.md              # This file
└── TEST_CASES.md            # Documented test runs and results
```

---

## 6. Setup Instructions

### 6.1 Clone and create a virtual environment
```bash
git clone <your-repo-url>
cd research_assistant
python -m venv venv
```
Activate it:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

### 6.2 Install dependencies
```bash
pip install -r requirements.txt --default-timeout=100
```

### 6.3 Get a Gemini API key
- Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- Create a free API key

### 6.4 Configure environment variables
Copy `.env.example` to `.env` and fill in your key:
```
GOOGLE_API_KEY=your_actual_key_here
```

### 6.5 Run the agent
```bash
python main.py
```

Type your question at the `You:` prompt. Type `exit` or `quit` to stop.

---

## 7. Tools

### 7.1 `web_search`
Searches the web via DuckDuckGo for current events, recent data, or anything the model
may not know confidently. Returns titles, links, and snippets so the agent can cite
real sources (not just the tool name).

### 7.2 `calculator`
Evaluates arithmetic expressions safely (restricted character set, no arbitrary code
execution). Used for percentages, growth calculations, and numeric comparisons, the
agent is instructed to never do math "in its head."

### 7.3 `file_reader`
Reads local `.pdf` or `.txt` files by path and returns their text content (capped at
5000 characters) for summarization or Q&A. This is something a plain chatbot **cannot
do**, it has no access to the local filesystem.

All three tools were tested individually to confirm the agent selects the *correct*
tool automatically based on question type (see `TEST_CASES.md`).

---

## 8. Comparison: Chatbot vs. RAG vs. Agent

A common misconception is that "chatbots don't search the web, agents do." In testing,
we found that modern consumer chatbots (like the Gemini web app) now perform **hidden**
web searches by default. So the real differentiator of an agent isn't *whether* it can
search, it's **transparency, control, and extensibility**.

| Capability | Basic Chatbot | RAG System | This Agent |
|---|---|---|---|
| Answers from static knowledge | ✅ | ✅ | ✅ |
| Searches the web | Sometimes (hidden, unauditable) | ❌ (searches only your documents) | ✅ (explicit, logged) |
| Reads your local files | ❌ | ✅ (its own document store) | ✅ (`file_reader`, any file by path) |
| Uses custom tools (calculator, APIs, etc.) | ❌ | ❌ | ✅ (fully extensible) |
| Reasoning visibility | ❌ black box | Partial (retrieved chunks visible) | ✅ full ReAct loop logged live |
| Structured, machine-readable output | ❌ | ❌ (usually prose) | ✅ validated Pydantic JSON |
| Multi-turn memory control | Managed by provider, opaque | Varies | ✅ explicit `thread_id`, inspectable |
| Customizable behavior/constraints | ❌ fixed | Partial | ✅ full system prompt control |
| Multi-step planning (search → calculate → search again) | ❌ | ❌ | ✅ |

**Real test:** we asked plain Gemini (gemini.google.com) to read `sample.txt` from the
local machine. Its response:

> "I don't have access to your computer's local files, so I can't open or read
> `sample.txt` directly... If you can copy and paste the text of the file here, or
> upload/attach the file to our chat, I would be happy to summarize it for you!"

Our agent handles this natively via `file_reader`, no manual copy-pasting required.

**Conclusion:** the value of an agent isn't that it can search, it's that its
reasoning is auditable, its tools are yours to define, and its output can plug
directly into other systems.

---

## 9. Known Limitations & Observations

- **Free-tier rate limits:** Gemini's free tier caps daily requests (as low as 20/day
  on some models during testing). Each user query can consume 2+ requests (one for
  tool-call decisions, one for structured output generation). This was caught as a
  real failure case during testing, see `TEST_CASES.md` for how it's handled.
- **"Anticipated" phrasing quirk:** the model sometimes phrases already-reported facts
  as "anticipated" or "expected" due to its own training cutoff bleeding into word
  choice, even when live search results confirm the event already happened. This is
  a phrasing quirk, not a factual error in the underlying data retrieved.
- **DuckDuckGo search quality:** free, no API key required, but results are sometimes
  less comprehensive than paid alternatives (e.g. Tavily, SerpAPI). Swappable in
  `tools.py` if higher-quality search is needed later.
- **In-memory checkpointer:** conversation memory resets when the program stops. For
  persistent memory across restarts, swap `InMemorySaver` for `SqliteSaver` or
  `PostgresSaver`.

---

## 10. Example Interaction

```
You: What are the latest breakthroughs in quantum computing in 2026?
[14:02:20] Agent received query, starting reasoning...
[14:02:22] Agent decided to call tool: web_search  args={'query': '...'}
[14:02:25] Tool result received: ...
[14:02:28] Agent finished reasoning. Preparing final answer.

ResearchBot:
Summary: In 2026, significant advancements are anticipated in quantum computing...
Key Findings:
 - ...
Sources: [actual URLs/titles]
Confidence: high
```

See `TEST_CASES.md` for the full set of documented test runs.

---

## 11. Author

**Syed Ahmad Ali Shah**
Generative AI Intern — GAIRL, KICS, NCAI
GitHub: [github.com/ahmadcodes39](https://github.com/ahmadcodes39)
