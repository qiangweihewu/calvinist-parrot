import streamlit as st
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.sql_models import ConversationHistory
from parrot_ai import chat_functions
from parrot_ai.v2_brain import interactWithAgents, load_selected_conversation, reset_status
from parrot_ai.ccel_index import display_consulted_sources
from PIL import Image

from dotenv import load_dotenv
load_dotenv()

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login()

from openai import OpenAI
client = OpenAI()

# Load the conversation history for the logged-in user and display it in the sidebar
def load_conversation_history(user_id):
    conversations = chat_functions.get_conversation_history(ConversationHistory, user_id)
    
    if len(conversations) == 0:
        st.sidebar.write("No conversations yet. I'm looking forward to chatting with you!")
    else:
        for idx, conversation in enumerate(conversations):
            if st.sidebar.button(conversation.conversation_name, key=f"conversation_button_{idx}"):
                # Load the selected conversation into st.session_state['messages']
                st.session_state['parrot_messages'] = conversation.messages
                load_selected_conversation()
                st.session_state['new_conversation'] = False
                st.session_state['conversation_name'] = conversation.conversation_name
                st.rerun()

clear_button = st.sidebar.button("New Conversation")
st.sidebar.divider()

if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as {st.session_state['username']}")
    st.sidebar.subheader("Chat History")
    with st.container():
        load_conversation_history(st.session_state['user_id'])
else:
    st.sidebar.write(f"Please log in to see your chat history.")

# to show chat history on ui
if "parrot_messages" not in st.session_state:
    reset_status()

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
        st.session_state["parrot_messages"].append({"role": "user", "avatar": "🧑‍💻", "content": prompt})
        interactWithAgents(prompt)
else:
    st.warning("Please log in to start a conversation.")
    st.write("Please use the sidebar to log in or register.")


if "page" not in st.session_state:
    st.session_state["page"] = "v2 Parrot"
if st.session_state.page != "v2 Parrot":
    st.session_state["page"] = "v2 Parrot"
    reset_status()

if clear_button:
    reset_status()