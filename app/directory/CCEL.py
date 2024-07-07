import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import parrot_ai.ccel_index as ccel
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.sql_models import CCELConversationHistory
from parrot_ai import chat_functions

load_dotenv()

parrot_icon = Image.open("app/calvinist_parrot.ico")
ccel_start = [
    {
        "role": "assistant",
        "avatar": parrot_icon,
        "content": "What do you want to learn?"
    }
]

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login()

# Setting up the session state
if "ccel_engine" not in st.session_state:
    st.session_state["ccel_engine"] = ccel.ccel_chat_engine()

if "page" not in st.session_state:
    st.session_state["page"] = "CCEL"
if st.session_state.page != "CCEL":
    st.session_state["page"] = "CCEL"
    st.session_state["ccel_messages"] = ccel_start

# Sidebar
clear_button = st.sidebar.button("New Conversation")
st.sidebar.divider()

if clear_button:
    st.session_state["ccel_messages"] = ccel_start
    st.rerun()

# to show chat history on ui
if "ccel_messages" not in st.session_state:
    st.session_state["ccel_messages"] = ccel_start

if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as {st.session_state['username']}")
    st.sidebar.subheader("Chat History")
    with st.container():
        chat_functions.load_conversation_history(
            CCELConversationHistory, 
            st.session_state['user_id'],
            'ccel_messages'
        )
else:
    st.sidebar.write(f"Please log in to see your chat history.")

chat_functions.load_conversation("ccel_messages")

if prompt := st.chat_input(placeholder="What is predestination?"):
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    with st.spinner("Thinking..."):
        response = st.session_state.ccel_engine.chat(prompt)
    st.chat_message("assistant", avatar=parrot_icon).write(response.response)
    with st.expander(f"📚 **Counsulted Sources**"):
        consulted_sources = ccel.parse_source_nodes(response.source_nodes)
        ccel.display_consulted_sources(consulted_sources)
    st.session_state["ccel_messages"].append({"role": "assistant", "avatar": parrot_icon, "content": response.response, "consulted_sources": consulted_sources})
