import os
import streamlit as st
from ai_parrot.CalvinistParrotAgent import CalvinistParrot
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Calvinist Parrot v2", 
    page_icon="💬",
    layout="wide",
    menu_items={
        'Get help': 'https://svrbc.org/',
        'About': "v2.1"
    }
)

@st.cache_resource
def loading_parrot():
    return CalvinistParrot()

custom_agent = loading_parrot()

class main_parrot:
    def __init__(self):
        self.im = Image.open("app/calvinist_parrot.ico")
        self.clear = st.sidebar.button("Reset chat history")
        st.sidebar.divider()
        if "steps" not in st.session_state:
            st.session_state["steps"] = {}

        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "avatar": self.im, "content": "What passage do you want to study?"}]

        self.executor, self.msgs = custom_agent.create_agent()

    def main(self):
        if "page" not in st.session_state:
            st.session_state["page"] = "Main Chat"
        if st.session_state.page != "Main Chat":
            st.session_state["page"] = "Main Chat"
            st.session_state["messages"] = [{"role": "assistant", "avatar": self.im, "content": "What theological questions do you have?"}]
            st.session_state["steps"] = {}

        if self.clear:
            st.session_state["messages"] = [{"role": "assistant", "avatar": self.im, "content": "What theological questions do you have?"}]
            self.msgs.add_ai_message("What theological questions do you have?")
            st.session_state["steps"] = {}

        for idx, msg in enumerate(st.session_state["messages"]):
            avatar_ = "🧑‍💻" if msg["role"] == "user" else self.im
            st.chat_message(msg["role"], avatar=avatar_).write(msg["content"])
            with st.expander(f"📚 **Additional information**"):
                for step in st.session_state.steps.get(str(idx), []):
                    if step[0].tool != "_Exception":
                        st.write(f"Category searched: {step[0].tool}, with input: {step[0].tool_input}")
                        st.write(f"{step[1]}")
                        st.divider()

        if prompt := st.chat_input(placeholder="What is predestination?"):
            st.chat_message("user", avatar="🧑‍💻").write(prompt)

            with st.chat_message("assistant", avatar=self.im):
                with st.spinner("Thinking..."):
                    response = self.executor(prompt)
                st.write(response["output"])
                with st.expander(f"📚 **Additional information**"):
                    for sources in response["intermediate_steps"]:
                        if sources[0].tool != "_Exception":
                            st.write(f"Category searched: {sources[0].tool}, with input: {sources[0].tool_input}")
                            st.write(f"{sources[1]}")
                            st.divider()
            st.session_state.steps[str(len(self.msgs.messages) - 1)] = response["intermediate_steps"]

if __name__ == "__main__":
    obj = main_parrot()
    obj.main()