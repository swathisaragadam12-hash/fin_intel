import os
import uuid

import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage

from config import REPORTS_DIR
from graph import compiled_agent


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="fin_intel Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 fin_intel Hub")
st.caption(
    "Personal Financial Intelligence Engine | Built using LangGraph, Gemini 2.5 Flash and Streamlit"
)


# -----------------------------
# Session State
# -----------------------------

if "graph_messages" not in st.session_state:
    st.session_state.graph_messages = []

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm fin_intel.\n\n"
                "Ask me about any company, stock or financial ratio."
            )
        }
    ]

# Every browser gets its own conversation
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.header("📂 Reports")

    pdf_files = []

    if os.path.exists(REPORTS_DIR):
        pdf_files = sorted(
            [
                file
                for file in os.listdir(REPORTS_DIR)
                if file.endswith(".pdf")
            ],
            reverse=True
        )

    if pdf_files:

        latest_pdf = pdf_files[0]
        latest_path = os.path.join(REPORTS_DIR, latest_pdf)

        with open(latest_path, "rb") as pdf:

            st.download_button(
                label="📥 Download Latest Report",
                data=pdf,
                file_name=latest_pdf,
                mime="application/pdf"
            )

        if st.button("🗑 Delete Latest Report"):

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


# -----------------------------
# User Input
# -----------------------------

user_query = st.chat_input(
    "Ask about a company or request a financial report..."
)

if user_query:

    # Display user message

    st.session_state.ui_messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    st.session_state.graph_messages.append(
        HumanMessage(content=user_query)
    )

    # Generate response

    with st.chat_message("assistant"):

        with st.spinner("Analyzing..."):

            try:

                output = compiled_agent.invoke(
                    {
                        "messages": st.session_state.graph_messages
                    },
                    config={
                        "configurable": {
                            "thread_id": st.session_state.thread_id
                        }
                    }
                )

                st.session_state.graph_messages = output["messages"]

                assistant_reply = output["messages"][-1].content

                st.markdown(assistant_reply)

                st.session_state.ui_messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_reply
                    }
                )

                # Check only recent messages for PDF generation

                recent_messages = output["messages"][-5:]

                pdf_created = any(
                    isinstance(msg, ToolMessage)
                    and "SUCCESS: PDF report" in str(msg.content)
                    for msg in recent_messages
                )

                if pdf_created:

                    st.success("PDF report generated successfully!")

                    st.rerun()

            except Exception as e:

                st.error(
                    "Something went wrong while processing your request."
                )

                st.exception(e)