# graph.py
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from config import MODEL_NAME
from tools import all_tools

# 1. Define custom state to handle conversational buffers sequentially
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# 2. Bind the Gemini 2.5 Flash model with custom operational toolsets
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.2, max_retries=3)
llm_with_tools = llm.bind_tools(all_tools)

# 3. Node definition for LLM interaction
def call_model(state: AgentState) -> dict:
    """Node handler responsible for executing the agent's core model intelligence."""
    system_prompt = (
        "You are fin_intel, an expert financial analyst. "
        "When a user asks for a report or PDF of a company (e.g., 'generate pdf report of apple'), "
        "you must follow a strict 2-step pipeline without asking for permission:\n"
        "1. First, call `get_stock_analysis` to fetch the real-time company metrics.\n"
        "2. Second, take that retrieved financial data, format it cleanly, and immediately "
        "call `generate_pdf_report` to write the file.\n\n"
        "CRITICAL: Output clear, professional conversational text only. "
        "Never return raw list objects, text dictionaries, or metadata signatures to the user."
    )
    messages = [HumanMessage(content=system_prompt)] + list(state["messages"])
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 4. Conditional Edge Router to check for tool requirements
def should_continue(state: AgentState) -> str:
    """Conditional routing block checking if the model requested specific tool call execution loops."""
    last_message = state["messages"][-1]
    # If the model requested functional actions, keep loop open and route towards the tools node
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    # End conversational process node transitions
    return END

# 5. Build and compile the state graph sequence pipeline
workflow = StateGraph(AgentState)

# Add processing nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(all_tools))

# Establish relational edge routes
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

# Compile graph asset to execute locally inside application modules
compiled_agent = workflow.compile()