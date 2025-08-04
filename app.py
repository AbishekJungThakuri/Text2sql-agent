import streamlit as st
from text2sql import SQLAgent 
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize agent once
@st.cache_resource
def get_agent():
    return SQLAgent(db_path="/home/dell/DS Projects/Text2sql-agent/database/school.db")

agent = get_agent()

# Streamlit page setup
st.set_page_config(page_title="SQL Chat Agent", layout="centered")
st.title("🧠💬 SQL Chat Agent")
st.caption("Ask natural language questions and get answers from your database!")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box
user_input = st.text_input("Enter your question:", key="input")

# Submit button
if st.button("Ask") and user_input.strip():
    with st.spinner("Thinking..."):
        result = agent.query(user_input)

        # Store in history
        st.session_state.chat_history.append({
            "question": user_input,
            "sql_query": result.get("sql_query"),
            "answer": result.get("answer"),
        })

# Display chat history
if st.session_state.chat_history:
    st.subheader("💬 Chat History")
    for idx, chat in enumerate(reversed(st.session_state.chat_history), 1):
        with st.expander(f"🔹 Q{len(st.session_state.chat_history) - idx + 1}: {chat['question']}"):
            st.markdown(f"**Answer:**\n{chat['answer'] or 'No answer found.'}")
