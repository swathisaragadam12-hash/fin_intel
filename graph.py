from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from config import MODEL_NAME
from tools import all_tools

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.2)
llm_with_tools = llm.bind_tools(all_tools)

# -------------------------------
# System Prompt
# -------------------------------

system_prompt = """
You are fin_intel, an AI financial analyst.

Your job is to help users understand companies, stock performance,
financial ratios, charts, and business fundamentals.

Guidelines:
- Always call the stock analysis tool ('get_stock_analysis') whenever the user asks about a company, stock, valuation, performance, trends, or explicitly requests a CHART or GRAPH.
- The stock analysis tool will automatically build a chart behind the scenes when called. Inform the user that the chart has been generated and displayed.
- If the user asks for a comparison between multiple companies, call the stock analysis tool separately for each company.
- Never make up financial data. If the tool cannot retrieve the information, politely explain the issue.
- When presenting financial information, explain what the numbers mean instead of simply listing them.
- If the user asks to create, save, download or export a report, first prepare a clean report summary and then call the PDF report tool.

INVESTMENT STRATEGY & ADVICE QUERIES:
If a user asks "should I invest in X?" or questions your investment outlook on a company:
1. Start with a brief, standard financial disclaimer noting you provide data-driven insights rather than personalized legal financial advice.
2. Structure your response clearly using Markdown formatting with these specific sections:
   - **Reasons to Consider Investing**: Highlight the company's competitive advantages (e.g., sector tailwinds, technological leadership, or strong financial metrics found in your data).
   - **Risks to Keep in Mind**: Balance your analysis with standard risks (e.g., market volatility, high valuation ratios like P/E or P/B, or industrial competition).
   - **Analyst View**: Summarize a practical investing framework split by time horizons (e.g., Long-term vs. Short-term strategy implications, or concepts like Dollar-Cost Averaging).

Keep your responses professional, scannable, balanced, and easy to understand.
"""

def call_model(state: AgentState):
    messages = [SystemMessage(content=system_prompt), *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(all_tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

compiled_agent = workflow.compile()