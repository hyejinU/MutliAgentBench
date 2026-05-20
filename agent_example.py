"""
BKMS1 Term Project: DB Doctor
LLM Agent Boilerplate (Anthropic Claude API)

This file demonstrates the basic structure of a tool-use agent loop.
Your job is to design the system prompt, tool definitions, and termination logic.

Install before use: pip install anthropic
Set API key:        export ANTHROPIC_API_KEY="your-key-here"
"""

import anthropic
import json
from db_connect import run_sql

# ================================================================
# 1. Create LLM Client
# ================================================================
client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from environment
MODEL = "claude-sonnet-4-20250514"

# ================================================================
# 2. System Prompt Design
# ================================================================
# TODO: Write your own system prompt.
# Hints:
#   - Clearly define the agent's role (e.g., "You are a PostgreSQL DBA")
#   - List which system views the agent can query
#   - Suggest an investigation strategy or order
#   - Instruct the agent to call submit_diagnosis when done

SYSTEM_PROMPT = """You are an experienced PostgreSQL DBA.
A production PostgreSQL database is experiencing performance issues.
Use the provided tools to diagnose the root cause.

Available tools:
- run_sql: Execute read-only SQL on the database. You can use SELECT, EXPLAIN, and SHOW statements.
- submit_diagnosis: Submit your final diagnosis.

Key system views you can query:
- pg_stat_statements: Per-query execution statistics
- pg_stat_activity: Currently running sessions
- pg_locks: Current lock state
- pg_stat_user_tables: Per-table statistics
- pg_stat_user_indexes: Per-index usage statistics

Investigate systematically, gather sufficient evidence, then submit your diagnosis.
"""

# ================================================================
# 3. Tool Definitions
# ================================================================
TOOLS = [
    {
        "name": "run_sql",
        "description": "Execute a read-only SQL query on PostgreSQL and return the result. Supports SELECT, EXPLAIN ANALYZE, and SHOW statements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "submit_diagnosis",
        "description": "Submit the final diagnosis. Only call this after gathering sufficient evidence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cause": {
                    "type": "string",
                    "description": "The diagnosed root cause (e.g., 'Lock Contention', 'Missing Index', 'Index Bloat')"
                },
                "evidence": {
                    "type": "string",
                    "description": "Summary of the evidence supporting the diagnosis"
                }
            },
            "required": ["cause", "evidence"]
        }
    }
    # TODO: Add more tools if needed.
]


# ================================================================
# 4. Tool Execution
# ================================================================
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatches a tool call to the actual function and returns the result."""
    if tool_name == "run_sql":
        return run_sql(tool_input["query"])
    elif tool_name == "submit_diagnosis":
        return json.dumps(tool_input, ensure_ascii=False)
    else:
        return f"ERROR: Unknown tool '{tool_name}'"


# ================================================================
# 5. Agent Loop
# ================================================================
def run_agent(user_message: str, max_turns: int = 15):
    """
    Runs the agent.

    Flow:
    1. Send a message to the LLM.
    2. If the LLM requests a tool call -> execute the tool, return the result -> go to 1.
    3. If the LLM responds without a tool call (or calls submit_diagnosis) -> done.
    """
    messages = [{"role": "user", "content": user_message}]
    turn = 0

    print(f"\n{'='*60}")
    print(f"[User] {user_message}")
    print(f"{'='*60}\n")

    while turn < max_turns:
        turn += 1
        print(f"--- Turn {turn}/{max_turns} ---")

        # Call the LLM
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Process the response
        # response.content may contain a mix of TextBlock and ToolUseBlock
        assistant_content = response.content

        # Print the LLM's text output
        for block in assistant_content:
            if block.type == "text" and block.text:
                print(f"[Agent] {block.text}")

        # Check stop reason
        if response.stop_reason == "end_turn":
            print("\n[Agent stopped] LLM ended the conversation.")
            break

        if response.stop_reason != "tool_use":
            print(f"\n[Agent stopped] stop_reason: {response.stop_reason}")
            break

        # Handle tool calls
        tool_results = []
        diagnosis_submitted = False

        for block in assistant_content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                tool_use_id = block.id

                print(f"  [Tool call] {tool_name}({json.dumps(tool_input, ensure_ascii=False)[:200]})")

                # Execute the tool
                result = execute_tool(tool_name, tool_input)
                print(f"  [Tool result] {result[:300]}{'...' if len(result) > 300 else ''}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": result,
                })

                if tool_name == "submit_diagnosis":
                    diagnosis_submitted = True

        # Append to conversation history
        messages.append({"role": "assistant", "content": assistant_content})
        messages.append({"role": "user", "content": tool_results})

        if diagnosis_submitted:
            print(f"\n{'='*60}")
            print("[Diagnosis submitted]")
            print(f"{'='*60}")
            # Give the LLM one more turn to provide a closing summary
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )
            for block in response.content:
                if block.type == "text" and block.text:
                    print(f"[Agent] {block.text}")
            break

    if turn >= max_turns:
        print(f"\n[Warning] Reached maximum turns ({max_turns}). Stopping.")

    return messages


# ================================================================
# 6. Entry Point
# ================================================================
if __name__ == "__main__":
    # Start the agent with an initial prompt
    # TODO: Modify the initial message if needed.
    conversation = run_agent(
        "The database is experiencing performance issues. Please investigate and find the root cause."
    )
