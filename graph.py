from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from config import MODEL_NAME
from tools import all_tools


# -------------------------------
# Graph State
# -------------------------------

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# -------------------------------
# LLM
# -------------------------------

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0.2
)

llm_with_tools = llm.bind_tools(all_tools)


# -------------------------------
# System Prompt
# -------------------------------

system_prompt = """
You are fin_intel, an AI financial analyst.

Your job is to help users understand companies, stock performance,
financial ratios and business fundamentals.

Guidelines:

- Use the stock analysis tool whenever the user asks about a company,
  stock, valuation, PE ratio, PB ratio, market cap or stock price.

- If the user asks for a comparison between multiple companies,
  call the stock analysis tool separately for each company.

- Never make up financial data.
  If the tool cannot retrieve the information,
  politely explain the issue.

- When presenting financial information,
  explain what the numbers mean instead of simply listing them.

- If the user asks to create, save, download or export a report,
  first prepare a clean report and then call the PDF tool.

Keep your responses professional, concise and easy to understand.
"""


# -------------------------------
# Agent Node
# -------------------------------

def call_model(state: AgentState):

    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"]
    ]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# -------------------------------
# Router
# -------------------------------

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


# -------------------------------
# Build Graph
# -------------------------------

workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(all_tools))

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

workflow.add_edge("tools", "agent")


compiled_agent = workflow.compile()