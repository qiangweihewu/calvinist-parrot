from sqlalchemy import Column, Integer, String, create_engine, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import pythonbible as bible
from bs4 import BeautifulSoup
import os, requests, llama_index
import pandas as pd

bsb = pd.read_csv('app/bsb.tsv', sep='\t')

load_dotenv()

gpt_model = os.environ.get("GPT_MODEL")

import google_connector as gc

# create engine
pool = gc.connect_with_connector('parrot_db')
Base = declarative_base()

# if temp folder doesn't exist create it
if not os.path.exists('temp'):
    os.makedirs('temp')

# create table
class NewVerse(Base):
    __tablename__ = 'new_verses'
    verse_id = Column(Integer, primary_key=True)
    bible_hub_url = Column(String)
    verse_text = Column(Text)
    commentary = Column(Text)

    def __repr__(self):
        return f"<NewVerse(verse_id='{self.verse_id}', bible_hub_url='{self.bible_hub_url}', verse_text='{self.verse_text}', commentary='{self.commentary}')>"

# create the table in the database
Base.metadata.create_all(pool)

# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_commentary_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    maintable2 = soup.find('div', {'class': 'maintable2'})
    jump_div = maintable2.find('div', {'id': 'jump'})
    jump_div.extract()
    return maintable2.get_text()

def get_bsb_text(verse):
    return bsb.loc[bsb['Verse'] == verse, 'Berean Standard Bible'].values[0]

def add_verse(references):
    # create session
    Session = sessionmaker(bind=pool)

    # create a new verse
    for i in references:
        verse_id = bible.convert_reference_to_verse_ids(i)
        book = str(i.book).lower().split('.')[1]
        book = book.split('_')[1] + '_' + book.split('_')[0] if '_' in book else book
        for j in verse_id:
            session = Session()
            reference = bible.convert_verse_ids_to_references([j])
            bible_hub_url = f"https://biblehub.com/commentaries/{book}/{reference[0].start_chapter}-{reference[0].start_verse}.htm"
            commentary_text = get_commentary_text(bible_hub_url)

            new_verse = NewVerse(
                verse_id=j, 
                bible_hub_url=bible_hub_url, 
                verse_text=bible.get_verse_text(j),
                commentary=commentary_text
            )

            # add the new verse to the session
            session.add(new_verse)

            # commit the transaction
            session.commit()

            # close the session
            session.close()

def check_if_verse_exists(verse_id):
    # create session
    Session = sessionmaker(bind=pool)
    session = Session()

    # query the new_verses table
    verse = session.query(NewVerse).filter(NewVerse.verse_id == verse_id).first()

    # close the session
    session.close()

    if verse is not None:
        return verse.commentary
    else:
        new_ref = bible.convert_verse_ids_to_references([verse_id])
        add_verse(new_ref) # We get the commentaries from BibleHub and add them to the database
        return check_if_verse_exists(verse_id)

def get_commentary_from_db(references):
    bsb_text = ''
    for i in references:
        verse_id = bible.convert_reference_to_verse_ids(i)
        reference_out = bible.format_scripture_references([i])
        for j in verse_id:
            ref = bible.convert_verse_ids_to_references([j])
            temp_ref = bible.format_scripture_references(ref)
            ref = ref[0]
            text_ = f'\n{ref.start_chapter}.{ref.start_verse} - {check_if_verse_exists(j)}'
            with open(f'temp/{temp_ref}.txt', 'w', encoding="utf-8") as f:
                f.write(text_)
            try:
                bsb_text += f'{get_bsb_text(temp_ref)}  \n'
                version = 'BSB'
            except:
                bsb_text += f'{bible.get_verse_text(j)}  \n'
                version = 'ASV'
        bsb_text = bsb_text[:-1]
        bsb_text += f' - {reference_out} ({version})  \n\n'
        # print(os.listdir('temp'))
    return bsb_text

def check_input(input_):
    references = bible.get_references(input_)
    if len(references) == 0:
        return None
    else:
        bsb_text = get_commentary_from_db(references)
        return bsb_text
    

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

import nest_asyncio

nest_asyncio.apply()

llm = OpenAI(
    model=gpt_model,
    temperature=0
)

Settings.llm = llm
Settings.embed_model = OpenAIEmbedding()

# Using the LlamaDebugHandler to print the trace of the sub questions
# captured by the SUB_QUESTION callback event type
llama_debug = LlamaDebugHandler(print_trace_on_end=True)
callback_manager = CallbackManager([llama_debug])

Settings.callback_manager = callback_manager

def generate_query_index(text_ref):
    documents = SimpleDirectoryReader('temp').load_data()
    
    vector_query_engine = VectorStoreIndex.from_documents(
        documents,
        use_async=True,
    ).as_query_engine()

    # setup base query engine as tool
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="Commentaries from BibleHub",
                description=f"Commentaries from BibleHub on {text_ref}",
            ),
        ),
    ]

    query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=query_engine_tools,
        use_async=True,
    )

    return query_engine
