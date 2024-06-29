import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import parrot_ai.bible_commentaries as btk

load_dotenv()

parrot_icon = Image.open("app/calvinist_parrot.ico")
clear_button = st.sidebar.button("Reset chat history")
st.sidebar.divider()
if "query_engine" not in st.session_state:
    st.session_state["query_engine"] = None

# to show chat history on ui
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What passage do you want to study?"}]

if "check" not in st.session_state:
    st.session_state["check"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "Study Helper"
if st.session_state.page != "Study Helper":
    st.session_state["page"] = "Study Helper"
    st.session_state["messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What passage do you want to study?"}]
    st.session_state["query_engine"] = None
    st.session_state["check"] = None

if clear_button:
    st.session_state["messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What passage do you want to study?"}]
    st.session_state["query_engine"] = None

for msg in st.session_state["messages"]:
    avatar_ = "🧑‍💻" if msg["role"] == "user" else parrot_icon
    st.chat_message(msg["role"], avatar=avatar_).write(msg["content"])
    if "sources" in msg.keys():
        with st.expander(f"📚 **Additional information**"):
            for n, source in enumerate(msg["sources"]):
                st.write(f"  \nSource {n+1}:  \n\t{source.text}")

prompt = st.chat_input(placeholder="Can you help me understand this passage?")

if prompt:
    st.session_state.messages.append({"role": "user", "avatar": "🧑‍💻", "content": prompt})
    st.chat_message("user", avatar="🧑‍💻").write(prompt)

    if st.session_state.query_engine is None:
        with st.spinner("Fetching commentaries..."):
            st.session_state.check = btk.check_input(prompt)
        if st.session_state.check is None:
            response_temp = "Sorry, I couldn't find any references in your input. Please try again."
            st.chat_message("assistant", avatar=parrot_icon).write(response_temp)
            st.session_state.messages.append({"role": "assistant", "avatar": parrot_icon, "content": response_temp})
        else:
            st.chat_message("assistant", avatar=parrot_icon).write(st.session_state.check)
            with st.spinner("Indexing commentaries..."):
                text_ref = st.session_state.check.split(" - ")[-1].replace("  \n\n", "")
                st.session_state.query_engine = btk.generate_query_index(text_ref)
            response_temp = "Commentaries indexed! What question do you have?"
            st.chat_message("assistant", avatar=parrot_icon).write(response_temp)
            st.session_state.messages.append({"role": "assistant", "avatar": parrot_icon, "content": st.session_state.check})
            st.session_state.messages.append({"role": "assistant", "avatar": parrot_icon, "content": response_temp})
    else:
        with st.spinner("Thinking..."):
            response = st.session_state.query_engine.query(prompt)
        st.chat_message("assistant", avatar=parrot_icon).write(response.response)
        with st.expander(f"📚 **Excerpts from Sources**"):
            for n, source in enumerate(response.source_nodes):
                if source.text.startswith("Sub question:"):
                    new_text = source.text.replace("Sub question:", "  \n**Sub question:**").replace("Response:", "  \n**Response:**")
                    st.write(f"  \n**Source {n+1}:**  \n{new_text}")
                else:
                    st.write(f"  \n**Source {n+1}:**  \n{source.text}")
        st.session_state.messages.append({"role": "assistant", "avatar": parrot_icon, "content": response.response, "sources": response.source_nodes})

if st.session_state["query_engine"] is None:
    st.sidebar.write("❌ - We don't have a Query Engine...")
else:
    st.sidebar.write(f"✅ - We have a Query Engine Active!  \n\n{st.session_state.check}")