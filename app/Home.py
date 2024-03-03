import streamlit as st
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.EncryptedCookieManager_v2 import EncryptedCookieManager
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

im = Image.open("app/calvinist_parrot.ico")

st.set_page_config(
    page_title="Calvinist Parrot v2.3", 
    page_icon=im,
    layout="wide",
    menu_items={
        'Get help': 'https://svrbc.org/',
        'About': "v2.3\n\nCreated by: [Jesús Mancilla](mailto:jesus@jgmancilla.com)\n\nFrom [SVRBC](https://svrbc.org/)\n\n"
    }
)

# get secret key from .env
secret_key = os.getenv("SECRET_KEY")

# This should be on top of your script
cookies = EncryptedCookieManager(
    # This prefix will get added to all your cookie names.
    # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
    prefix="ktosiek/streamlit-cookies-manager/",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password=os.environ.get("COOKIES_PASSWORD", secret_key),
)

if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.spinner()
    st.stop()

if 'token' in cookies:
    token = cookies['token']
    user = auth.validate_session(token)

if "page" not in st.session_state:
    st.session_state['page'] = 'Main'

# Setup the UI
st.image("https://cultofthepartyparrot.com/parrots/hd/calvinist_parrot.gif",width=100)

if user:
    st.title(f"Welcome back to the Calvinist Parrot, {user.name}!")
else:
    st.title("Welcome to the Calvinist Parrot!")
st.write("I'm here to help you explore and understand the Bible through the lens of Reformed theology. Ask me any questions about the Scriptures, and I'll provide answers based on my knowledge and understanding.  \n\nI'm an AI-driven application. Using the 'Study Helper', I draw information from the [Bible Hub](https://biblehub.com/commentaries).")
st.write("ESV didn't let me use their API because they are not 'approving the pairing of the ESV text with AI-generated text.' Therefore, we use the Berean Standard Bible ([BSB](https://berean.bible/)) as our main translation. You can find more information about it [here](https://copy.church/initiatives/bibles/).")

st.divider()

st.write("""
👈 On the menu on the left, you can see all the tools you can use, like:
- **[Study Helper](https://calvinistparrot.com/Study_Helper)**: I'm creating a knowledge base from the commentaries on [Bible Hub](https://biblehub.com/commentaries). Ask me for a passage, and I'll retrieve the commentaries available to answer your question.
- **[Devotionals](https://calvinistparrot.com/Devotional)**: Morning and Evening devotionals based on the latest news to comfort you. Remember, AI generates these 😉.
- **[v1 Parrot](https://calvinistparrot.com/v1_Parrot)**: This is the old version of the parrot. It has a lot of personality, and I missed chatting with it.
""")

st.divider()

st.write("""
Feb 2024 update: Due to lack of funding, I'm depricating the "Main Chat" since the cost to maintain the CCEL index is too high. I'm sorry for the inconvenience. I'll keep the "Study Helper" and "Devotionals" tools available. I'm also working on a new tool to help you study the Bible. Stay tuned!
""")

st.markdown("I'm still learning, so please be patient with me! I'm always looking to improve, so if you have any feedback, <a href='mailto:jesus@jgmancilla.com'>please let me know</a>", unsafe_allow_html=True)
#   \n\nI'm also open source, so if you're interested in contributing to my development, check out my [GitHub](https://github.com/Jegama/calvinist-parrot)

# TODO: Add a link to the github repo