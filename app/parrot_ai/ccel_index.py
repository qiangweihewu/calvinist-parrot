from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from llama_index.core import VectorStoreIndex, StorageContext
from parrot_ai.cutomPGVectorStore import PGVectorStore
from parrot_ai.core.prompts import CCEL_CHAT_SYS_PROMPT

import os

from dotenv import load_dotenv
load_dotenv()

gpt_model = os.environ.get("GPT_MODEL")

llm = OpenAI(
    model=gpt_model,
    temperature=0
)

Settings.llm = llm
Settings.embed_model = OpenAIEmbedding(model='text-embedding-3-small')

vector_store = PGVectorStore.from_params(
    table_name="ccel_vector_store"
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

ccel_index = VectorStoreIndex([], storage_context=storage_context)

def ccel_chat_engine():
    return ccel_index.as_chat_engine(
        chat_mode="react",
        similarity_top_k=5,
        system_prompt=CCEL_CHAT_SYS_PROMPT,
    )
