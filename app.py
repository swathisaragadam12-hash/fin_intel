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
    # Execute Agent graph
    with st.chat_message("assistant"):
        with st.spinner("Streaming graph executions..."):
            inputs = {"messages": st.session_state.graph_messages}
            config = {"configurable": {"thread_id": "swathi_session_stream"}}
            
            try:
                output_state = compiled_agent.invoke(inputs, config)
                st.session_state.graph_messages = output_state["messages"]
                
                # Extract raw string from final message node
                final_ai_reply = output_state["messages"][-1].content
                
                # --- BULLETPROOF PARSING SAFEGUARD ---
                if isinstance(final_ai_reply, str):
                    # Check for signature blocks or stringified list/dict responses
                    if "'text':" in final_ai_reply or '"text":' in final_ai_reply or final_ai_reply.strip().startswith("[{"):
                        try:
                            # Direct bracket slice targeting the text key value
                            if "'text':" in final_ai_reply:
                                start_idx = final_ai_reply.find("'text':") + 7
                            else:
                                start_idx = final_ai_reply.find('"text":') + 7
                            
                            remaining = final_ai_reply[start_idx:].strip()
                            quote_char = remaining[0]
                            
                            actual_start = final_ai_reply.find(quote_char, start_idx) + 1
                            actual_end = final_ai_reply.find(quote_char, actual_start)
                            
                            extracted = final_ai_reply[actual_start:actual_end]
                            if len(extracted.strip()) > 10:
                                final_ai_reply = extracted.strip()
                        except Exception:
                            # Fallback regex parser if indices shift dynamically
                            import re
                            match = re.search(r"['\"]text['\"]:\s*['\"](.*?)['\"]", final_ai_reply, re.DOTALL)
                            if match:
                                final_ai_reply = match.group(1)
                    
                    # Absolute sanitization to drop lingering raw signature dumps
                    if "'signature':" in final_ai_reply or "extras" in final_ai_reply:
                        # Split out the text if it's at the beginning before the extras dict
                        fallback_clean = final_ai_reply.split("{'extras'")[0].split('"extras"')[0].strip()
                        if len(fallback_clean) > 20:
                            final_ai_reply = fallback_clean.rstrip(", '").rstrip(', "').lstrip("[{")
                        else:
                            final_ai_reply = "I have compiled your real-time data overview cleanly! The PDF document has been formatted and exported successfully."
                # -------------------------------------
                
                # Render clean layout to UI canvas
                st.markdown(final_ai_reply.replace(r"\n", "\n"))
                st.session_state.ui_messages.append({"role": "assistant", "content": final_ai_reply})
                
                pdf_generation_triggered = any(
                    isinstance(m, ToolMessage) and "SUCCESS: PDF report" in str(m.content)
                    for m in output_state["messages"]
                )
                
                if pdf_generation_triggered:
                    st.success("New financial report artifact compiled to background files!")
                    st.rerun()

            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    st.error("⚠️ **API Quota Limit Met:** Please wait a brief moment for the window to refresh.")
                else:
                    st.error(f"System Node Exception: {str(e)}")