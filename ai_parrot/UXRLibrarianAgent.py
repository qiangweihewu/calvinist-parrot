import os, llama_index
import numpy as np
from langchain.agents import AgentExecutor
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.tools import Tool
from llama_index import LangchainEmbedding, ServiceContext, StorageContext
from llama_index.indices.loading import load_index_from_storage

from CustomEngine import refine_template, text_qa_template
from CustomConversationalChatAgent import ConversationalChatAgent

from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.environ.get("azure_api_key")
os.environ["OPENAI_API_BASE"] = os.environ.get("azure_endpoint")
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_TYPE"] = "azure"

from trulens_eval import TruLlama, Feedback, Tru, feedback
tru = Tru()
openai = feedback.AzureOpenAI(model_engine = "gpt-35-turbo", deployment_id = "gpt-35-turbo")

# Question/answer relevance between overall question and answer.
f_qa_relevance = Feedback(openai.relevance).on_input_output()

# Question/statement relevance between question and each context chunk.
f_qs_relevance = Feedback(openai.qs_relevance).on_input().on(
    TruLlama.select_source_nodes().node.text
).aggregate(np.mean)

# Setup the index
llm = AzureChatOpenAI(deployment_name="gpt-35-turbo", temperature=0)

embedding_llm = LangchainEmbedding(
    OpenAIEmbeddings(
        model="text-embedding-ada-002",
        deployment="text-embedding-ada-002",
        openai_api_key=os.environ["OPENAI_API_KEY"],
        openai_api_base=os.environ["OPENAI_API_BASE"],
        openai_api_type=os.environ["OPENAI_API_TYPE"],
        openai_api_version=os.environ["OPENAI_API_VERSION"],
    ),
    embed_batch_size=1,
)

service_context = ServiceContext.from_defaults(
    chunk_size_limit=1024, 
    llm=llm, 
    embed_model=embedding_llm
)

llama_index.set_global_service_context(service_context)

class load_index:
    def __init__(self):
        librarian_storage_context = StorageContext.from_defaults(persist_dir='librarian_vector_index')
        librarian_index = load_index_from_storage(librarian_storage_context)
        librarian_query_engine = librarian_index.as_query_engine(
            similarity_top_k=10,
            text_qa_template=text_qa_template, 
            refine_template=refine_template
        )
        self.tru_query_engine = TruLlama(
            librarian_query_engine,
            app_id='UXR_Librarian',
            feedbacks=[f_qa_relevance, f_qs_relevance]
        )

    def formater(self, response):
        texts = []
        texts.append(response.response)
        report = []
        for source_node in response.source_nodes:
            if source_node.node.metadata['title'] not in report:
                report.append(source_node.node.metadata['title'])
                source_text = f"Report: [{source_node.node.metadata['title']}]({source_node.node.metadata['report_url']})  \nLast update: {source_node.node.metadata['last_modified']}"
                if 'pdf_name' in source_node.node.metadata.keys():
                    if source_node.node.metadata['pdf_name'] not in report:
                        report.append(source_node.node.metadata['pdf_name'])
                        source_text += f"  \nPDF Name: {source_node.node.metadata['pdf_name']}  \nPage: {source_node.node.metadata['page']}  \n[PDF Link]({source_node.node.metadata['pdf_url']})"
                    else:
                        source_text += f"Page: {source_node.node.metadata['page']}"
                elif "pptx_name" in source_node.node.metadata.keys():
                    if source_node.node.metadata['pptx_name'] not in report:
                        report.append(source_node.node.metadata['pptx_name'])
                        source_text += f"  \nPPTX Name: {source_node.node.metadata['pptx_name']}  \nSlide: {source_node.node.metadata['slide']}  \n[PPTX Link]({source_node.node.metadata['pptx_url']})"
                    else:
                        source_text += f"Slide: {source_node.node.metadata['slide']}"
                texts.append(source_text)
            else:
                if 'pdf_name' in source_node.node.metadata.keys():
                    if source_node.node.metadata['pdf_name'] not in report:
                        report.append(source_node.node.metadata['pdf_name'])
                        source_text = f"  \nPDF Name: {source_node.node.metadata['pdf_name']}  \nPage: {source_node.node.metadata['page']}  \n[PDF Link]({source_node.node.metadata['pdf_url']})"
                    else:
                        source_text = f"  \nPage: {source_node.node.metadata['page']}"
                elif "pptx_name" in source_node.node.metadata.keys():
                    if source_node.node.metadata['pptx_name'] not in report:
                        report.append(source_node.node.metadata['pptx_name'])
                        source_text = f"PPTX Name: {source_node.node.metadata['pptx_name']}  \nSlide: {source_node.node.metadata['slide']}  \n[PPTX Link]({source_node.node.metadata['pptx_url']})"
                    else:
                        source_text = f"Slide: {source_node.node.metadata['slide']}"
                else:
                    continue
                texts.append(source_text)
        return "\n\n".join(texts)
    
    def query(self, question):
        response = self.tru_query_engine.query(question)
        return self.formater(response)
    
class RokuCustomAgent():
    def __init__(self):
        self.vector_index = load_index()
    
    def create_agent(self):
        msgs = StreamlitChatMessageHistory()
        memory = ConversationBufferMemory(
            chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
        )

        tools = [
            Tool(
                name="UXR_Librarian",
                func=self.vector_index.query,
                description="Main knowledge base for all the UX Research conducted at Roku since Aug 2021"
            )
        ]

        chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)

        executor = AgentExecutor.from_agent_and_tools(
            agent=chat_agent,
            tools=tools,
            memory=memory,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            verbose=True
        )
        return executor, msgs