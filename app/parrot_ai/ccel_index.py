import streamlit as st
from llama_index.core import VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from llama_index.core import VectorStoreIndex, StorageContext
from parrot_ai.cutomPGVectorStore import PGVectorStore
from parrot_ai.core.prompts import CCEL_CHAT_SYS_PROMPT

import os

from dotenv import load_dotenv
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

def display_consulted_sources(consulted_sources):
    for k, source in consulted_sources.items():
        pages = ", ".join(source["pages"])
        st.write(f"  \n**Book:** {source['website']}")
        st.write(f"Author: {source['author']} ({source['date']})")
        st.write(f"Pages: {pages}")
        st.write(f"{source['pdf']}")
        st.divider()

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

def ccel_chat_engine(parrot_history = []):
    return ccel_index.as_chat_engine(
        chat_mode="react",
        similarity_top_k=5,
        system_prompt=CCEL_CHAT_SYS_PROMPT,
        chat_history=parrot_history,
    )

def generate_query_4_ccel_agent(current_conversation):
    ccel_agent_prompt = f"""I'm have this conversation:

---------------------
{current_conversation}
---------------------

Based on it, what follow up information do you think is relevant for the user to know? Please explain in simple words the key topics based on what you found in the CCEL."""
    
    return ccel_agent_prompt

def create_ccel_agent():
    ccel_engine = ccel_index.as_query_engine(
        similarity_top_k=5,
    )

    query_engine_tools = [
        QueryEngineTool(
            query_engine=ccel_engine,
            metadata=ToolMetadata(
                name="ccel_engine", description="Provides information from the Christian Classics Ethereal Library (CCEL) that contains a vast library of classic Christian texts."
            ),
        )
    ]

    agent = ReActAgent.from_tools(
        query_engine_tools,
        llm=llm, 
    )
    return agent