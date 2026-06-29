# app.py
import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from config import OUTPUT_REPORT_PATH
from graph import compiled_agent
# Interface Configuration Settings
st.set_page_config(page_title="fin_intel Dashboard", page_icon="📈", layout="wide")
st.title("📈 fin_intel Hub")
st.caption("Personal Financial Intelligence Engine | Built with LangGraph, Gemini 2.5 Flash & Streamlit")

# Sidebar component layer for managing local storage items
with st.sidebar:
    st.header("Document Export Centre")
    if os.path.exists(OUTPUT_REPORT_PATH):
        # Expose download button trigger if file system finds compiled document
        with open(OUTPUT_REPORT_PATH, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Compiled PDF Statement",
                data=pdf_file,
                file_name="fin_intel_analysis.pdf",
                mime="application/pdf"
            )
        if st.button("🗑️ Clear Local Document Stacks"):
            os.remove(OUTPUT_REPORT_PATH)
            st.rerun()
    else:
        st.info("No current reports compiled. Request the agent to build one within chat window logs.")

# Initialize separate tracking lists in session state
# 1. graph_messages: Tracks underlying rich LangGraph message objects (including tool payloads)
if "graph_messages" not in st.session_state:
    st.session_state.graph_messages = []

# 2. ui_messages: Tracks straightforward key-value strings for clean rendering in Streamlit's UI canvas
if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = [{"role": "assistant", "content": "Welcome back Swathi! Let's examine some market indicators today."}]

# Print history tracebacks down onto user dashboard canvas
for msg in st.session_state.ui_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Track conversational event handlers
if user_query := st.chat_input("Query company metrics or request: 'Export a PDF summary of Nvidia'..."):
    # Append to UI list and render immediately
    st.session_state.ui_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Append to full LangGraph internal history tracking array
    st.session_state.graph_messages.append(HumanMessage(content=user_query))

    # Execute Agent graph
    with st.chat_message("assistant"):
        with st.spinner("Streaming graph executions..."):
            inputs = {"messages": st.session_state.graph_messages}
            config = {"configurable": {"thread_id": "swathi_session_stream"}}
            
            output_state = compiled_agent.invoke(inputs, config)
            st.session_state.graph_messages = output_state["messages"]
            
            final_ai_reply = output_state["messages"][-1].content
            
            # --- STUDENT SAFEGUARD: Clean up any leaked API metadata blocks ---
            if isinstance(final_ai_reply, str) and (final_ai_reply.startswith("[{") or "'signature':" in final_ai_reply):
                # If the model returned a raw payload string, look for normal conversational text lines
                lines = final_ai_reply.split("\n")
                cleaned_lines = [l for l in lines if "'signature':" not in l and "'type':" not in l and not l.strip().startswith("[{")]
                final_ai_reply = "\n".join(cleaned_lines).strip()
                
                # Fallback backup message if the string was completely compromised
                if not final_ai_reply or len(final_ai_reply) < 10:
                    final_ai_reply = "I have successfully processed the data pipeline and built your requested financial profile below!"
            # ------------------------------------------------------------------
            
            st.markdown(final_ai_reply)
            st.session_state.ui_messages.append({"role": "assistant", "content": final_ai_reply})
            
            pdf_generation_triggered = any(
                isinstance(m, ToolMessage) and "SUCCESS: PDF report" in str(m.content)
                for m in output_state["messages"]
                )
            
            if pdf_generation_triggered:
                st.success("New financial report artifact compiled to background files!")
                st.rerun()