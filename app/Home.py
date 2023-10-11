import os
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

im = Image.open("app/calvinist_parrot.ico")

st.set_page_config(
    page_title="Calvinist Parrot v2.1", 
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': 'https://svrbc.org/',
        'About': "v2.1"
    }
)

if "page" not in st.session_state:
    st.session_state['page'] = 'Main'

# Setup the UI
st.image("https://cultofthepartyparrot.com/parrots/hd/calvinist_parrot.gif",width=100)
st.title("Welcome to the Calvinist Parrot v2.0!")
st.write("I'm here to help you explore and understand the Bible through the lens of Reformed theology. Ask me any questions you have about the Scriptures, and I'll provide answers based on my knowledge and understanding.  \n\nI'm no longer an 'AI Duo', but with the help of the Christian Classics Ethereal Library, I can now provide you with a wider range of insights and answers.")

st.divider()

st.write("""
On the menu on the left you can see all the tools you can use like:
- **Main Chat**: This is the main chat, you can interact with me and I'll get the knowledge from the CCEL.
- **Study Helper**: I'm creating a knowledge base from the commentaries available on [Bible Hub](https://biblehub.com/commentaries). Ask me for a pasage and I'll retrive the commentaries available there to answer your question.
- **Devotionals**: Devotionals comming soon!
""")

st.divider()

st.markdown("I'm still learning, so please be patient with me! I'm always looking to improve, so if you have any feedback, <a href='mailto:jgmancilla@svrbc.org'>please let me know</a>", unsafe_allow_html=True)
#   \n\nI'm also open source, so if you're interested in contributing to my development, check out my [GitHub](https://github.com/Jegama/calvinist-parrot)
