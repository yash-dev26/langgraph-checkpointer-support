from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.types import interrupt
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

load_dotenv()


@tool()
def human_interrupt_tool(query: str):
    """Request human assistance."""
    human_reply = interrupt({
        "query": query,
        "message": "The agent has requested human assistance. Please provide input to help the agent continue.",
    })  # graph will exit out and save data in DB
    return human_reply["data"]  # resume graph with human input

tools = [human_interrupt_tool]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools=tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tools_node = ToolNode(tools=tools)
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tools_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")  # after tool is done, go back to chatbot to get response from tool call
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

# doing this is good if we later decide to switch from mongo checkpointer to something else
def create_graph_chat(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

