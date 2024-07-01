import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import parrot_ai.ccel_index as ccel

load_dotenv()

parrot_icon = Image.open("app/calvinist_parrot.ico")
clear_button = st.sidebar.button("Reset chat history")
st.sidebar.divider()
if "ccel_engine" not in st.session_state:
    st.session_state["ccel_engine"] = ccel.ccel_chat_engine()

# to show chat history on ui
if "ccel_messages" not in st.session_state:
    st.session_state["ccel_messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What do you want to learn?"}]

if "page" not in st.session_state:
    st.session_state["page"] = "CCEL"
if st.session_state.page != "CCEL":
    st.session_state["page"] = "CCEL"
    st.session_state["ccel_messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What do you want to learn?"}]

if clear_button:
    st.session_state["ccel_messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What do you want to learn?"}]

for msg in st.session_state["ccel_messages"]:
    avatar_ = "🧑‍💻" if msg["role"] == "user" else parrot_icon
    st.chat_message(msg["role"], avatar=avatar_).write(msg["content"])
    if "consulted_sources" in msg.keys():
        with st.expander(f"📚 **Counsulted Sources**"):
            ccel.display_consulted_sources(msg["consulted_sources"])

prompt = st.chat_input(placeholder="What is predestination?")

if prompt:
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    with st.spinner("Thinking..."):
        response = st.session_state.ccel_engine.chat(prompt)
    st.chat_message("assistant", avatar=parrot_icon).write(response.response)
    with st.expander(f"📚 **Counsulted Sources**"):
        consulted_sources = ccel.parse_source_nodes(response.source_nodes)
        ccel.display_consulted_sources(consulted_sources)
    st.session_state.messages.append({"role": "assistant", "avatar": parrot_icon, "content": response.response, "consulted_sources": consulted_sources})
