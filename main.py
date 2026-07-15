from agent import agent
from datetime import datetime

def log(message: str):
    """Print a timestamped log line so the agent's reasoning is visible live."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_chat():
    print("ResearchBot ready. Type 'exit' to quit.\n")
    config = {"configurable": {"thread_id": "session-1"}}

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        log("Agent received query, starting reasoning...")

        final_chunk = None

        # stream_mode="updates" yields one chunk per node/step as it happens
        for chunk in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            stream_mode="updates",
        ):
            for node_name, node_output in chunk.items():
                messages = node_output.get("messages", [])
                for msg in messages:
                    msg_type = msg.__class__.__name__

                    if msg_type == "AIMessage":
                        if msg.tool_calls:
                            for tc in msg.tool_calls:
                                log(f"🔧 Agent decided to call tool: {tc['name']}  args={tc['args']}")
                        elif msg.text:
                            log(f"🤖 Agent reasoning/answer: {msg.text[:200]}")

                    elif msg_type == "ToolMessage":
                        preview = msg.text[:200] if msg.text else str(msg.content)[:200]
                        log(f"👀 Tool result received: {preview}...")

            final_chunk = chunk

        log("Agent received query, starting reasoning...")

        final_chunk = None

        try:
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
                stream_mode="updates",
            ):
                for node_name, node_output in chunk.items():
                    messages = node_output.get("messages", [])
                    for msg in messages:
                        msg_type = msg.__class__.__name__

                        if msg_type == "AIMessage":
                            if msg.tool_calls:
                                for tc in msg.tool_calls:
                                    log(f"🔧 Agent decided to call tool: {tc['name']}  args={tc['args']}")
                            elif msg.text:
                                log(f"🤖 Agent reasoning/answer: {msg.text[:200]}")

                        elif msg_type == "ToolMessage":
                            preview = msg.text[:200] if msg.text else str(msg.content)[:200]
                            log(f"👀 Tool result received: {preview}...")

                final_chunk = chunk

        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                print("\nResearchBot: I've hit the API rate limit for now. "
                      "Please wait about a minute and try again.\n")
            else:
                log(f"⚠️ Unexpected error: {error_str[:200]}")
                print("\nResearchBot: Something went wrong while processing that. "
                      "Please try rephrasing your question.\n")
            continue

        log("Agent finished reasoning. Preparing final answer.\n")


if __name__ == "__main__":
    run_chat()