import os, llama_index
from ai_parrot.CustomConversationalChatAgent import ConversationalChatAgent
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from llama_index import ServiceContext

from ai_parrot.ccelTools import toolkit

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-4", 
    temperature=0
)

llm_embeddings = OpenAIEmbeddings()

service_context = ServiceContext.from_defaults(
    llm=llm, embed_model=llm_embeddings
)

llama_index.set_global_service_context(service_context)

with open('urls to the query engines.txt', 'r') as f:
    urls = f.read().split('\n')

with open('index_summary.txt', 'r') as f:
    index_summary = f.read().split('\n')

class CalvinistParrot():
    def create_agent(self):
        msgs = StreamlitChatMessageHistory()
        memory = ConversationBufferMemory(
            chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
        )

        chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=toolkit)

        executor = AgentExecutor.from_agent_and_tools(
            agent=chat_agent,
            tools=toolkit,
            memory=memory,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            verbose=True
        )
        return executor, msgs