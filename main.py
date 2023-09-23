import os, llama_index
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from llama_index import ServiceContext, StorageContext
from llama_index.indices.loading import load_index_from_storage
from pydantic import BaseModel

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

ccel_storage_context = StorageContext.from_defaults(persist_dir='app/ccel_index')
ccel_index = load_index_from_storage(
    ccel_storage_context
    )
ccel_query_engine = ccel_index.as_query_engine(
    response_mode='refine',
    similarity_top_n=5
)

class Question(BaseModel):
    question: str

@app.post("/query")
def query(input: Question):
    response = ccel_query_engine.query(input.question)
    return response