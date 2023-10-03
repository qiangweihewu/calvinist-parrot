import os, time, requests, base64
import streamlit as st

from langchain.callbacks import StreamlitCallbackHandler

from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")

def CCELQueryEngine(question):
    response = requests.post(
        "http://127.0.0.1:80/query", 
        headers={"Content-Type": "application/json"}, 
        json={"question": question}
    )
    return response.json()

st.set_page_config(
    page_title="Calvinist Parrot 🦜", 
    page_icon="🦜",
    layout="wide",
    # initial_sidebar_state="expanded"
)

@st.cache_resource
def waking_up_the_parrot():
    # search = SerpAPIWrapper()
    # search.run

    query_engine_tools = [
        Tool.from_function(
            func=CCELQueryEngine,
            name="ccel_library",
            description="Provides access to most of the books in the Christian Classics Ethereal Library.",
        )
    ]

    msgs = StreamlitChatMessageHistory()
    memory = ConversationBufferMemory(
        chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
    )
    llm = ChatOpenAI(
        model_name="gpt-4", 
        streaming=True,
        temperature=0
    )

    agent = initialize_agent(
        query_engine_tools, 
        llm,
        memory=memory,
        verbose=True,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, 
        handle_parsing_errors=True,
    )
    return agent, msgs

agent, msgs = waking_up_the_parrot()

file_ = open("calvinist_parrot.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

# Setup the UI
st.title("🦜 UXR Librarian - Roku [ALPHA]")
st.sidebar.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="Calvinist Parrot">',
    unsafe_allow_html=True
)
st.sidebar.title("Welcome to the UXR Librarian!")
st.sidebar.write("Welcome to the Calvinist Parrot chatbot. I'm here to help you explore and understand the Bible through the lens of Reformed theology. Ask me any questions you have about the Scriptures, and I'll provide answers based on my knowledge and looking into the Christian Classics Ethereal Library (CCEL).")
st.sidebar.divider()
st.sidebar.write("If you want to know more about the UXR Librarian, please contact [Jesus Mancilla](mailto\:jgmancilla@svrbc.org)")
st.sidebar.divider()
clear = st.sidebar.button("Reset chat history")

if len(msgs.messages) == 0 or clear:
    msgs.clear()
    msgs.add_ai_message("What theological question do you have?")

avatars = {"human": ["user", "🧑‍💻"], "ai": ["assistant", "🦜"]}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type][0], avatar=avatars[msg.type][1]):
        # Render intermediate steps if any were saved
        st.write(msg.content)
        # TODO - Add this back in
        # for step in st.session_state.steps.get(str(idx), []):
        #     if step[0].tool == "_Exception":
        #         continue
        #     with st.expander(f"📚 **Information from the Library**"):
        #         st.write(f"{step[1]}")
        #         st.divider()

if prompt := st.chat_input(placeholder="What theological question do you have?"):
    st.chat_message("user", avatar="🧑‍💻").write(prompt)

    with st.chat_message("assistant", avatar="🦜"):
        st_cb = StreamlitCallbackHandler(st.container())
        response = agent.run(prompt, callbacks=[st_cb])
        st.write(response)