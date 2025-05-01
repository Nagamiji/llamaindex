# # src/app.py
# import streamlit as st
# from llm_setup import get_chat_engine

# st.title("Department Chatbot")

# # 1) Initialize agent once
# if "chat_agent" not in st.session_state:
#     st.session_state.chat_agent = get_chat_engine()

# # 2) Chat history in session
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # 3) Render history
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # 4) New user input
# if prompt := st.chat_input("Ask a question about the department"):
#     # record user
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # 5) Talk to the agent synchronously
#     response = st.session_state.chat_agent.chat(prompt)

#     # 6) Display & record assistant
#     with st.chat_message("assistant"):
#         st.markdown(response)
#     st.session_state.messages.append({"role": "assistant", "content": response})
# src/app.py
import streamlit as st
import pandas as pd
from io import StringIO

from llm_setup import get_chat_engine
from tools import get_query_tool

st.set_page_config(page_title="Department Chatbot", layout="wide")
st.title("🎓 Department Chatbot")

# ——— Sidebar controls —————————————————————————————————————
with st.sidebar:
    st.markdown("### Actions")
    if st.button("🗑️ Clear chat"):
        st.session_state.pop("messages", None)
        st.session_state.pop("chat_agent", None)
        st.session_state.pop("sql_tool", None)
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("#### Examples")
    st.markdown("""
    - List all instructors and the classes they teach  
    - Who are the instructors in the Physics department?  
    - Find classes in Room 101 on Wednesday  
    - Update score for student 1 in subject 2 to 95  
    - Enroll 'Alice Brown' in 'Digital Systems'
    """, unsafe_allow_html=True)

# ——— Initialize agent & tools —————————————————————————————————
if "chat_agent" not in st.session_state:
    st.session_state.chat_agent = get_chat_engine()

if "sql_tool" not in st.session_state:
    st.session_state.sql_tool = get_query_tool()

# ——— Chat history —————————————————————————————————————————
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # render markdown or table snapshot
        if isinstance(msg.get("content"), pd.DataFrame):
            st.dataframe(msg["content"], use_container_width=True)
        else:
            st.markdown(msg["content"])

# ——— User input ——————————————————————————————————————————
prompt = st.chat_input("Ask a question about the department")

if prompt:
    # record user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1) Try raw SQL/Data mode
    rows = None
    try:
        with st.spinner("🔍 Running data query…"):
            rows = st.session_state.sql_tool.query_engine.query(prompt)
    except Exception:
        rows = None

    if isinstance(rows, list) and rows:
        # 2) Show table & download
        df = pd.DataFrame(rows)
        with st.chat_message("assistant"):
            st.markdown("✅ Here are the results I found:")
            st.dataframe(df, use_container_width=True)
            # prepare CSV
            csv_buf = StringIO()
            df.to_csv(csv_buf, index=False)
            st.download_button(
                label="📥 Download results as CSV",
                data=csv_buf.getvalue(),
                file_name="results.csv",
                mime="text/csv"
            )
        # store DataFrame object (for persistence)
        st.session_state.messages.append({"role": "assistant", "content": df})
    else:
        # 3) Fallback to LLM agent
        with st.spinner("🤖 Generating response…"):
            response = st.session_state.chat_agent.chat(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
