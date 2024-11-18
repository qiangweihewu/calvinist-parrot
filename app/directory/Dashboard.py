import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

import google_connector as gc
from sqlalchemy.orm import sessionmaker
from app.parrot_toolkit.sql_models import ChainReasoning, ConversationsCategories

# create engine
pool = gc.connect_with_connector('parrot_db')
SessionLocal = sessionmaker(bind=pool)

# Function to parse sql data into a dataframe
def parse_sql_data(data, keys):
    data_dict = {k: [] for k in keys}
    for d in data:
        for k in keys:
            data_dict[k].append(getattr(d, k))

    df = pd.DataFrame(data_dict)
    # df['reviewed_answer'] = df['reviewed_answer'].apply(lambda x: x.replace("\n", " "))
    return df

# Load ChainReasoning categories
chain_keys = ["chain_id", "user_question", "category", "subcategory", "issue_type", "reviewed_answer", "language", "timestamp"]
db = SessionLocal()
categories = db.query(ChainReasoning).all()
db.close()

chain_reasoning_df = parse_sql_data(categories, chain_keys)

# Load ConversationsCategories categories
conversations_keys = ["conversation_category_id", "user_question", "category", "subcategory", "issue_type", "reviewed_answer", "language", "parrot_type", "timestamp"]
db = SessionLocal()
conversations = db.query(ConversationsCategories).all()
db.close()

conversations_df = parse_sql_data(conversations, conversations_keys)

# Display the dataframes
st.title("Parrot AI Dashboard")

# Summary Statistics
st.subheader("Summary Statistics")
st.write(f"Chain Reasoning Categories: {chain_reasoning_df.shape[0]}")
st.write(f"Conversations Categories: {conversations_df.shape[0]}")