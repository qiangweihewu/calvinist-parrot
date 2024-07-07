import streamlit as st
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.sql_models import ConversationHistory
from parrot_ai import chat_functions
from parrot_ai.v2_brain import interactWithAgents, reset_status
from parrot_ai.ccel_index import display_consulted_sources
from PIL import Image

from dotenv import load_dotenv
load_dotenv()

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login()

# Setting up the session state
if "page" not in st.session_state:
    st.session_state["page"] = "v2 Parrot"

if st.session_state.page != "v2 Parrot":
    st.session_state["page"] = "v2 Parrot"
    reset_status()

# Sidebar
clear_button = st.sidebar.button("New Conversation")
st.sidebar.divider()

if clear_button:
    reset_status()

# to show chat history on ui
if "parrot_messages" not in st.session_state:
    reset_status()

if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as {st.session_state['username']}")
    st.sidebar.subheader("Chat History")
    with st.container():
        chat_functions.load_conversation_history(
            ConversationHistory, 
            st.session_state['user_id'],
            'parrot_messages'
        )
else:
    st.sidebar.write(f"Please log in to see your chat history.")

# Main content
if st.session_state['logged_in']:
    st.write(f"You are logged in as {st.session_state['username']}.")
    for msg in st.session_state["parrot_messages"]:
        if msg["role"] == "parrot":
            avatar = parrot
        elif msg["role"] == "calvin":
            avatar = calvin
        elif msg["role"] == "librarian":
            avatar = "👨‍🏫"
        else:
            avatar = "🧑‍💻"
        st.chat_message(msg["role"], avatar=avatar).write(msg["content"])
        if "consulted_sources" in msg.keys():
            with st.expander(f"📚 **Counsulted Sources**"):
                display_consulted_sources(msg["consulted_sources"])

    if prompt := st.chat_input(placeholder="What is predestination?"):
        st.chat_message("user", avatar="🧑‍💻").write(prompt)
        st.session_state["parrot_messages"].append(
            {"role": "user", "avatar": "🧑‍💻", "content": prompt}
        )
        interactWithAgents(prompt)
else:
    st.warning("Please log in to start a conversation.")
    st.write("Please use the sidebar to log in or register.")