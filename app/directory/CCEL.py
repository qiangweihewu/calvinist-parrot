import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.sql_models import CCELConversationHistory
from parrot_ai import chat_functions
import parrot_ai.ccel_index as ccel

load_dotenv()
parrot_icon = Image.open("app/calvinist_parrot.ico")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login()

# Setting up the language
if 'language' not in st.session_state:
    if st.session_state['logged_in'] == False:
        if st.session_state['url'] == 'loro':
            st.session_state['language'] = 'Español'
        else:
            st.session_state['language'] = 'English'

if st.session_state['language'] in ['Español', 'Spanish']:
    from parrot_toolkit.spanish_text import *
else:
    from parrot_toolkit.english_text import *

# Load session state
if "page" not in st.session_state:
    st.session_state["page"] = "CCEL"
if st.session_state["page"] != "CCEL":
    st.session_state["page"] = "CCEL"

ccel_start = [
    {
        "role": "assistant",
        "content": CCEL_FIRST_MESSAGE
    }
]

def reset_chat():
    st.session_state["ccel_messages"] = ccel_start
    st.session_state["chat_engine_chat_history"] = chat_functions.parse_parrot_messages(st.session_state["ccel_messages"])
    st.session_state["ccel_engine"] = ccel.ccel_chat_engine(st.session_state["chat_engine_chat_history"])
    st.session_state['new_conversation'] = True
    st.rerun()

# to show chat history on ui
if "ccel_messages" not in st.session_state:
    reset_chat()

# Setting up the session state
if "ccel_engine" not in st.session_state:
    st.session_state["ccel_engine"] = ccel.ccel_chat_engine(st.session_state["chat_engine_chat_history"])

# Sidebar
clear_button = st.sidebar.button(CLEAR_CHAT)
st.sidebar.divider()

if clear_button:
    reset_chat()

if st.session_state['logged_in']:
    st.sidebar.write(f"{LOGGED_AS} {st.session_state['username']}")
    st.sidebar.subheader(CHAT_HIST)
    with st.container():
        chat_functions.load_conversation_history(
            CCELConversationHistory, 
            st.session_state['user_id'],
            'ccel_messages'
        )
else:
    st.sidebar.write(NOT_LOGGED)

chat_functions.load_conversation("ccel_messages")

if prompt := st.chat_input(placeholder=CHAT_PLACESHOLDER):
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    st.session_state["ccel_messages"].append({"role": "user", "content": prompt})
    with st.spinner(SH_SPINNER_QUERY):
        response = st.session_state.ccel_engine.chat(prompt)
    st.chat_message("assistant", avatar=parrot_icon).write(response.response)
    with st.expander(CONSULTED_SOURCES):
        consulted_sources = ccel.parse_source_nodes(response.source_nodes)
        ccel.display_consulted_sources(consulted_sources)
    st.session_state["ccel_messages"].append({"role": "assistant", "content": response.response, "consulted_sources": consulted_sources})

    # Generate conversation name if it's a new conversation
    if st.session_state['new_conversation']:
        conversation_name = chat_functions.generate_conversation_name(st.session_state["ccel_messages"])
        if conversation_name:
            st.session_state['new_conversation'] = False
            st.session_state['conversation_name'] = conversation_name

    # Save the conversation
    chat_functions.create_or_update_conversation(
        CCELConversationHistory, 
        st.session_state['user_id'], 
        st.session_state['conversation_name'],
        st.session_state["ccel_messages"]
    )
    st.rerun()