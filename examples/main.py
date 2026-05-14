"""Minimal AgentAPI example."""

from agentapi import Agent, AgentAPI , tool

app = AgentAPI()

agent = Agent(
    system_prompt="You are a helpful assistant",
    provider="openai",
)

agent2 = Agent(
    system_prompt="You are a chess master who loves to teach chess", 
    provider="openai",
)

@app.chat("/chat")
async def chat(message: str):
    return await agent.run(message)


@app.chat("/stream")
async def stream_chat(message: str):
    return agent.stream(message)

@tool
def get_date():
    from datetime import datetime

    return datetime.now().isoformat()