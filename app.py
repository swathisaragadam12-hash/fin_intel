import os
import uuid
import ast
import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage

from config import REPORTS_DIR
from graph import compiled_agent

st.set_page_config(page_title="fin_intel Dashboard", page_icon="📈", layout="wide")
st.title("📈 fin_intel Hub")
st.caption("Personal Financial Intelligence Engine | Built using LangGraph, Gemini 2.5 Flash and Streamlit")

if "graph_messages" not in st.session_state:
    st.session_state.graph_messages = []

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = [
        {"role": "assistant", "content": "Hi! I'm fin_intel.\n\nAsk me about any company, stock or financial ratio."}
    ]

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("📂 Reports")
    pdf_files = []
    if os.path.exists(REPORTS_DIR):
        pdf_files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")], reverse=True)

    if pdf_files:
        latest_pdf = pdf_files[0]
        latest_path = os.path.join(REPORTS_DIR, latest_pdf)
        with open(latest_path, "rb") as pdf:
            st.download_button(label="📥 Download Latest Report", data=pdf.read(), file_name=latest_pdf, mime="application/pdf")
        if st.button("🗑 Delete Latest Report", use_container_width=True):
            os.remove(latest_path)
            st.rerun()
    else:
        st.info("No reports generated yet.")

# -----------------------------
# Display Previous Chat
# -----------------------------
for message in st.session_state.ui_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "chart" in message and os.path.exists(message["chart"]):
            st.image(message["chart"])

# -----------------------------
# User Input & Processing
# -----------------------------
user_query = st.chat_input("Ask about a company or request a financial report...")

if user_query:
    st.session_state.ui_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    st.session_state.graph_messages.append(HumanMessage(content=user_query))

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                output = compiled_agent.invoke(
                    {"messages": st.session_state.graph_messages},
                    config={"configurable": {"thread_id": st.session_state.thread_id}}
                )
                st.session_state.graph_messages = output["messages"]
                
                # Fetch raw message content
                last_message = output["messages"][-1]
                assistant_reply = last_message.content

                # Unpack list response wrappers into pure text to prevent showing raw dictionary objects
                if isinstance(assistant_reply, list):
                    clean_text = ""
                    for part in assistant_reply:
                        if isinstance(part, dict) and "text" in part:
                            clean_text += part["text"]
                        elif hasattr(part, "text"):
                            clean_text += part.text
                        else:
                            clean_text += str(part)
                    assistant_reply = clean_text
                elif not isinstance(assistant_reply, str):
                    assistant_reply = str(assistant_reply)

                st.markdown(assistant_reply)

                # Check back through tool execution nodes to parse chart path safely
                chart_to_display = None
                for msg in reversed(output["messages"]):
                    if isinstance(msg, ToolMessage) and "Chart Path" in str(msg.content):
                        try:
                            tool_data = ast.literal_eval(msg.content)
                            if isinstance(tool_data, dict) and tool_data.get("Chart Path"):
                                chart_to_display = tool_data["Chart Path"]
                                break
                        except:
                            pass

                if chart_to_display and os.path.exists(chart_to_display):
                    st.image(chart_to_display)

                ui_entry = {"role": "assistant", "content": assistant_reply}
                if chart_to_display:
                    ui_entry["chart"] = chart_to_display
                st.session_state.ui_messages.append(ui_entry)

                recent_messages = output["messages"][-5:]
                pdf_created = any(isinstance(msg, ToolMessage) and "SUCCESS: PDF report" in str(msg.content) for msg in recent_messages)

                if pdf_created:
                    st.success("PDF report generated successfully!")
                    st.rerun()

            except Exception as e:
                st.error("Something went wrong while processing your request.")
                st.exception(e)