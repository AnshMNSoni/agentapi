# AgentAPI

AgentAPI is a lightweight framework for building agentic AI backends with a familiar Python/FastAPI style.

## What You Get

- A stateful `Agent` with memory and tool calling
- Provider abstraction for OpenAI, Gemini, and OpenRouter
- Simple web API layer using `AgentAPI`
- Built-in streaming support through Server-Sent Events (SSE)
- CLI commands to scaffold and run projects

## Core Concepts

### `Agent`

`Agent` handles prompt orchestration, model calls, tool execution, and conversation memory.

### `AgentAPI`

`AgentAPI` extends FastAPI with chat-focused decorators:

- `@app.chat` for regular or streaming responses
- `@app.stream` as a streaming-only compatibility alias

### `@tool`

Mark plain Python functions as LLM-callable tools. AgentAPI builds provider-compatible tool schemas automatically.

## Orchestrating Multiple Agents

AgentAPI can coordinate multiple agents in one app, even when they use different providers or different memory backends.

Common patterns:

- Run agents in parallel and merge results with `asyncio.gather()`
- Assign each agent a separate provider for specialized behavior
- Give each agent its own `memory` instance to isolate conversations
- Create unlimited `InMemoryMemory` instances for local dev/testing with zero conflicts
- Use one agent as a tool inside another agent for delegated reasoning

```python
import asyncio
from agentapi import Agent, AgentAPI, InMemoryMemory, RedisMemory, create_conversation_id

app = AgentAPI()

conversation_id = create_conversation_id()

research_agent = Agent(
    system_prompt="You are a research assistant.",
    provider="openai",
    memory=RedisMemory(redis_url="redis://localhost:6379", conversation_id=conversation_id),
)

editor_agent = Agent(
    system_prompt="You are a concise editor.",
    provider="gemini",
    memory=InMemoryMemory(conversation_id=create_conversation_id()),
)


@app.post("/orchestrate")
async def orchestrate(message: str):
    research_task, edit_task = await asyncio.gather(
        research_agent.run(message),
        editor_agent.run(message),
    ) 

    '''
    To run sequentially depending on the use case:
    research_task = await research_agent.run(message)
    editor_task = await editor_agent.run(message)
    '''

    return {
        "research": research_task,
        "editor": edit_task,
        "combined": f"Research:\n{research_task}\n\nEditor:\n{edit_task}",
    }
```

This pattern works well when you want:

- one agent to draft while another critiques
- a fast local agent to handle routing while a stronger cloud model handles final answers
- different tenants or sessions to remain isolated with separate memory objects

## Quick Example

```python
from agentapi import Agent, AgentAPI

app = AgentAPI()

agent = Agent(
    system_prompt="You are a helpful assistant",
    provider="openai",
)


@app.chat("/chat")
async def chat(message: str):
    return await agent.run(message)


@app.chat("/stream")
async def stream_chat(message: str):
    return agent.stream(message)
```

## Next Steps

1. Start with [Installation](installation.md)
2. Follow [Getting Started](getting-started.md)
3. Configure [Providers](providers.md)
4. Read [Memory](memory.md)
5. Add [Tool Calling](tools.md)
