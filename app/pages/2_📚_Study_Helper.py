import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import parrot_toolkit.bible_commentaries as btk

load_dotenv()

st.set_page_config(
    page_title="Study Helper", 
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': 'https://svrbc.org/',
        'About': "v2.2\n\nCreated by: [Jesús Mancilla](mailto:jgmancilla@svrbc.org)\n\nFrom [SVRBC](https://svrbc.org/)\n\n"
    }
)

class study_helper:
    def __init__(self):
        self.im = Image.open("app/calvinist_parrot.ico")
        self.clear = st.sidebar.button("Reset chat history")
        st.sidebar.divider()
        if "query_engine" not in st.session_state:
            st.session_state["query_engine"] = None

        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "avatar": self.im, "content": "What passage do you want to study?"}]

        if "check" not in st.session_state:
            st.session_state["check"] = None

    def main(self):
        if "page" not in st.session_state:
            st.session_state["page"] = "Study Helper"
        if st.session_state.page != "Study Helper":
            st.session_state["page"] = "Study Helper"
            st.session_state["messages"] = [{"role": "assistant", "avatar": self.im, "content": "What passage do you want to study?"}]
            st.session_state["query_engine"] = None
            st.session_state["check"] = None

        if self.clear:
            st.session_state["messages"] = [{"role": "assistant", "avatar": self.im, "content": "What passage do you want to study?"}]
            st.session_state["query_engine"] = None

        for msg in st.session_state["messages"]:
            avatar_ = "🧑‍💻" if msg["role"] == "user" else self.im
            st.chat_message(msg["role"], avatar=avatar_).write(msg["content"])
            if "sources" in msg.keys():
                with st.expander(f"📚 **Additional information**"):
                    for n, source in enumerate(msg["sources"]):
                        st.write(f"  \nSource {n+1}:  \n\t{source.text}")

        prompt = st.chat_input(placeholder="I want to learn about Romans 9")

        if prompt:
            st.session_state.messages.append({"role": "user", "avatar": "🧑‍💻", "content": prompt})
            st.chat_message("user", avatar="🧑‍💻").write(prompt)

            if st.session_state.query_engine is None:
                with st.spinner("Fetching commentaries..."):
                    st.session_state.check = btk.check_input(prompt)
                if st.session_state.check is None:
                    response_temp = "Sorry, I couldn't find any references in your input. Please try again."
                    st.chat_message("assistant", avatar=self.im).write(response_temp)
                    st.session_state.messages.append({"role": "assistant", "avatar": self.im, "content": response_temp})
                else:
                    st.chat_message("assistant", avatar=self.im).write(st.session_state.check)
                    with st.spinner("Indexing commentaries..."):
                        st.session_state.query_engine = btk.generate_query_index()
                    response_temp = "Commentaries indexed! What question do you have?"
                    st.chat_message("assistant", avatar=self.im).write(response_temp)
                    st.session_state.messages.append({"role": "assistant", "avatar": self.im, "content": st.session_state.check})
                    st.session_state.messages.append({"role": "assistant", "avatar": self.im, "content": response_temp})
            else:
                    with st.spinner("Thinking..."):
                        response = st.session_state.query_engine.query(prompt)
                    st.chat_message("assistant", avatar=self.im).write(response.response)
                    with st.expander(f"📚 **Excerpts from Sources**"):
                        for n, source in enumerate(response.source_nodes):
                            st.write(f"  \nSource {n+1}:  \n\t{source.text}")
                    st.session_state.messages.append({"role": "assistant", "avatar": self.im, "content": response.response, "sources": response.source_nodes})

        if st.session_state["query_engine"] is None:
            st.sidebar.write("❌ - We don't have a Query Engine...")
        else:
            st.sidebar.write(f"✅ - We have a Query Engine Active!  \n{st.session_state.check}")
                    

if __name__ == "__main__":
    obj = study_helper()
    obj.main()