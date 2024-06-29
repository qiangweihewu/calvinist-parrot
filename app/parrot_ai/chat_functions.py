import streamlit as st
import re, os, datetime
import pandas as pd
import pythonbible as bible
import google_connector as gc
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt
from dotenv import load_dotenv
load_dotenv()

pool = gc.connect_with_connector('parrot_db')
SessionLocal = sessionmaker(bind=pool)

bsb = pd.read_csv('app/bsb.tsv', sep='\t')

def get_bsb_text(verse):
    return bsb.loc[bsb['Verse'] == verse, 'Berean Standard Bible'].values[0]

gpt_model = os.environ.get("GPT_MODEL")

from openai import OpenAI
client = OpenAI()

def get_response(messages_list, stream=True):
    response = client.chat.completions.create(
        model=gpt_model,
        messages=messages_list,
        stream=stream,
        temperature = 0
    )
    return response

def extractQuestions(text):
    pattern = r"\/\/(.*?)\/\/"
    questions = re.findall(pattern, text)
    return questions

def generate_conversation_name(current_conversation):
    prompt_create_name = f"""I have this conversation:

---------------------
{current_conversation}
---------------------

What would you like to name this conversation? It can be a short name to remember this conversation.

Please reply in the following JSON format:

{{
    "name": string \\ Name of the conversation
}}

Always return response as JSON."""


    get_name_prompt = [
        {"role": "system", "content": 'You are a helpful assistant that can create short names for conversations.'}, {"role": "user", "content": prompt_create_name}
    ]

    response = client.chat.completions.create(
        model=gpt_model,
        response_format={ "type": "json_object" },
        messages=get_name_prompt,
        temperature = 0
    )
    conversation_name = response.choices[0].message.content
    try:
        conversation_name = eval(conversation_name)['name']
        return conversation_name
    except:
        return None

# Create or update conversation history in the database
def create_or_update_conversation(conversation_table, user_id, conversation_name, messages):
    db = SessionLocal()
    try:
        # Check if the conversation already exists
        conversation = db.query(conversation_table).filter(
            conversation_table.user_id == user_id, 
            conversation_table.conversation_name == conversation_name
        ).first()

        if conversation:
            # Update the conversation
            conversation.messages = messages
            conversation.timestamp = dt.now(datetime.UTC)
        else:
            # Create a new conversation
            new_conversation = conversation_table(
                user_id=user_id, 
                conversation_name=conversation_name, 
                messages=messages
            )
            db.add(new_conversation)
        db.commit()
    except Exception as e:
        st.error(f"Error updating or creating conversation: {e}")
    finally:
        db.close()

def get_conversation_history(conversation_table, user_id):
    db = SessionLocal()
    try:
        conversations = db.query(conversation_table).filter(
            conversation_table.user_id == user_id
        ).order_by(conversation_table.timestamp.desc()).all()
    except Exception as e:
        st.error(f"Error getting conversation history: {e}")
    finally:
        db.close()
    return conversations