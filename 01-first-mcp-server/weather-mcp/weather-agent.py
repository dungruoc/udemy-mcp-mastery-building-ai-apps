from langchain_ollama.chat_models import ChatOllama
from langchain.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import BaseTool
from langfuse.langchain import CallbackHandler
from typing_extensions import TypedDict, Annotated

from dotenv import load_dotenv
import operator
import os, sys
import asyncio

load_dotenv()

ollama_base_url = 'http://localhost:11434'

chat_model = 'qwen3.5:9b-mlx'

llm = ChatOllama(
    base_url=ollama_base_url,
    model=chat_model,
    validate_model_on_init=True,
    temperature=0.8
)

async def get_tools():

    client = MultiServerMCPClient({
        "weather": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http"
        }
    })


    tools = await client.get_tools()
    return tools

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]


async def agent_node(agent_state: AgentState):
    tools = await get_tools()
    llm_with_tools = llm.bind_tools(tools)

    response = llm_with_tools.invoke(agent_state["messages"])
    return {'messages': [response]}


async def create_agent(tools: list[BaseTool], checkpointer=None):
    builder = StateGraph(AgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "agent")
    builder.add_edge("tools", "agent")
    builder.add_conditional_edges("agent", tools_condition)

    return builder.compile(checkpointer=checkpointer)


async def main(argv: list[str]):
    tools = await get_tools()
    print(tools)
    agent = await create_agent(tools)
    query = " ".join(argv)
    print(query)
    response = await agent.ainvoke({'messages': [HumanMessage(query)]})
    print(response['messages'][-1].content)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))