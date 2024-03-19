import os, llama_index
import dill as pickle # dill is a more powerful version of pickle
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from llama_index import ServiceContext
from pydantic import BaseModel
# from llama_index.llms import ChatMessage, MessageRole
# from llama_index.prompts import ChatPromptTemplate
from llama_index.indices.loading import load_index_from_storage

load_dotenv('app/.env')

app = FastAPI()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", 
    temperature=0
)

llm_embeddings = OpenAIEmbeddings()

service_context = ServiceContext.from_defaults(
    llm=llm, embed_model=llm_embeddings
)

llama_index.set_global_service_context(service_context)

# # Text QA Prompt
# chat_text_qa_msgs = [
#     ChatMessage(
#         role=MessageRole.SYSTEM,
#         content="Always answer the question. If the context isn't helpful, try again.",
#     ),
#     ChatMessage(
#         role=MessageRole.USER,
#         content=(
#             "Context information is below.\n"
#             "---------------------\n"
#             "{context_str}\n"
#             "---------------------\n"
#             "Given the context information and not prior knowledge, "
#             "answer the question: {query_str}\n"
#         ),
#     ),
# ]
# text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

# # Refine Prompt
# chat_refine_msgs = [
#     ChatMessage(
#         role=MessageRole.SYSTEM,
#         content="Always answer the question. If the context isn't helpful, try again.",
#     ),
#     ChatMessage(
#         role=MessageRole.USER,
#         content=(
#             "We have the opportunity to refine the original answer "
#             "(only if needed) with some more context below.\n"
#             "------------\n"
#             "{context_msg}\n"
#             "------------\n"
#             "Given the new context, refine the original answer to better "
#             "answer the question: {query_str}. "
#             "If the context isn't useful, output the original answer again.\n"
#             "Original Answer: {existing_answer}"
#         ),
#     ),
# ]
# refine_template = ChatPromptTemplate(chat_refine_msgs)

with open('precomputed_results/ccel_storage_context.pkl', 'rb') as f:
    ccel_storage_context = pickle.load(f)

ccel_index = load_index_from_storage(ccel_storage_context)
ccel_query_engine = ccel_index.as_query_engine(
    similarity_top_k=10
)

class Question(BaseModel):
    question: str

@app.post("/query")
def query(input: Question):
    response = ccel_query_engine.query(input.question)
    return response
