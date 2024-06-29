import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import parrot_ai.ccel_index as ccel

load_dotenv()

def parse_source_nodes(source_nodes):
    consulted_sources = {}
    for source in source_nodes:
        file_name = source.metadata['file_name'][:-4]
        if file_name not in consulted_sources.keys():
            pdf_link = f"[PDF]({source.metadata['pdf_link']})"
            book_website = f"[{source.metadata['title']}]({source.metadata['url']})"
            consulted_sources[file_name] = {
                "pdf": pdf_link,
                "website": book_website,
                "author": source.metadata['author'],
                "date": source.metadata['date'],
                "pages": [source.metadata['page_label']]
            }
        else:
            consulted_sources[file_name]["pages"].append(source.metadata['page_label'])
    return consulted_sources

parrot_icon = Image.open("app/calvinist_parrot.ico")
clear_button = st.sidebar.button("Reset chat history")
st.sidebar.divider()
if "ccel_engine" not in st.session_state:
    st.session_state["ccel_engine"] = ccel.ccel_chat_engine()

# to show chat history on ui
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What do you want to learn?"}]

if "page" not in st.session_state:
    st.session_state["page"] = "CCEL"
if st.session_state.page != "CCEL":
    st.session_state["page"] = "CCEL"
    st.session_state["messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What do you want to learn?"}]

if clear_button:
    st.session_state["messages"] = [{"role": "assistant", "avatar": parrot_icon, "content": "What do you want to learn?"}]

for msg in st.session_state["messages"]:
    avatar_ = "🧑‍💻" if msg["role"] == "user" else parrot_icon
    st.chat_message(msg["role"], avatar=avatar_).write(msg["content"])
    if "consulted_sources" in msg.keys():
        with st.expander(f"📚 **Additional information**"):
            for k, source in msg["consulted_sources"].items():
                pages = ", ".join(source["pages"])
                st.write(f"  \nBook {source['book_website']}")
                st.write(f"Author: {source['author']} ({source['date']})")
                st.write(f"Pages: {pages}")
                st.write(f"{source['pdf']}")

prompt = st.chat_input(placeholder="What is predestination?")

if prompt:
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    with st.spinner("Thinking..."):
        response = st.session_state.ccel_engine.chat(prompt)
    st.chat_message("assistant", avatar=parrot_icon).write(response.response)
    with st.expander(f"📚 **Sources**"):
        consulted_sources = parse_source_nodes(response.source_nodes)
        for k, source in consulted_sources.items():
            pages = ", ".join(source["pages"])
            st.write(f"  \n**Book:** {source['website']}")
            st.write(f"Author: {source['author']} ({source['date']})")
            st.write(f"Pages: {pages}")
            st.write(f"{source['pdf']}")
            st.divider()
    st.session_state.messages.append({"role": "assistant", "avatar": parrot_icon, "content": response.response, "consulted_sources": consulted_sources})
