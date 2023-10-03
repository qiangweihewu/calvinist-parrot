from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st
from ai_parrot.CalvinistParrotAgent import CalvinistParrot
from PIL import Image

im = Image.open("calvinist_parrot.ico")

st.set_page_config(
    page_title="Calvinist Parrot v2.0", 
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def loading_parrot():
    return CalvinistParrot()

custom_agent = loading_parrot()
executor, msgs = custom_agent.create_agent()

# Setup the UI
st.title("🦜 Calvinist Parrot v2.0")
st.sidebar.image("https://cultofthepartyparrot.com/parrots/hd/calvinist_parrot.gif",width=100)
st.sidebar.title("Welcome to the Calvinist Parrot v2.0!")
st.sidebar.write("I'm here to help you explore and understand the Bible through the lens of Reformed theology. Ask me any questions you have about the Scriptures, and I'll provide answers based on my knowledge and understanding.  \n\nI'm no longer an 'AI Duo', but with the help of the Christian Classics Ethereal Library, I can now provide you with a wider range of insights and answers.")
st.sidebar.markdown("I'm still learning, so please be patient with me! I'm always looking to improve, so if you have any feedback, <a href='mailto:jgmancilla@svrbc.org'>please let me know</a>", unsafe_allow_html=True)
#   \n\nI'm also open source, so if you're interested in contributing to my development, check out my [GitHub](https://github.com/Jegama/calvinist-parrot)
st.sidebar.divider()
clear = st.sidebar.button("Reset chat history")
st.sidebar.divider()
dev = st.sidebar.toggle("Dev Mode", False)

if len(msgs.messages) == 0 or clear:
    msgs.clear()
    msgs.add_ai_message("What theological questions do you have?")
    st.session_state.steps = {}
    st.session_state.feedback = False

avatars = {"human": ["user", "🧑‍💻"], "ai": ["assistant", im]}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type][0], avatar=avatars[msg.type][1]):
        # Render intermediate steps if any were saved
        st.write(msg.content)
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.expander(f"📚 **Additional information**"):
                st.write(f"Tool used: {step[0].tool}, with input: {step[0].tool_input}")
                st.write(f"{step[1]}")
                st.divider()

if prompt := st.chat_input(placeholder="What is predestination?"):
    st.chat_message("user", avatar="🧑‍💻").write(prompt)

    with st.chat_message("assistant", avatar=im):
        if dev:
            st_cb = StreamlitCallbackHandler(st.container())
            response = executor(prompt, callbacks=[st_cb])
        else:
            with st.spinner("Thinking..."):
                response = executor(prompt)
        st.write(response["output"])
        with st.expander(f"📚 **Additional information**"):
            for sources in response["intermediate_steps"]:
                if sources[0].tool != "_Exception":
                    st.write(f"Tool used: {sources[0].tool}, with input: {sources[0].tool_input}")
                    st.write(f"{sources[1]}")
                    st.divider()
    st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
    st.session_state.sources = ' - '.join([s[1].replace('\n', ' ').replace(',', ' ') for s in response['intermediate_steps']])
    st.session_state.response = response["output"].replace(',', ' ')
    st.session_state.prompt = prompt.replace(',', ' ')