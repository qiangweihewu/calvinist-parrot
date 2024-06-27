import streamlit as st
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.CookieManager import NEW_CM
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

st.set_page_config(
    page_title="Calvinist Parrot v2.4", 
    page_icon=parrot,
    layout="wide",
    menu_items={
        'Get help': 'https://svrbc.org/',
        'About': "v2.5\n\nCreated by: [Jesús Mancilla](mailto:jesus@jgmancilla.com)\n\nFrom [SVRBC](https://svrbc.org/)\n\n"
    }
)

cookie_manager = NEW_CM()

if cookie_manager.get_cookie():
    token = cookie_manager.get_cookie()
    user = auth.validate_session(token)
    if user:
        st.session_state['logged_in'] = True
        st.session_state['username'] = user.username
        st.session_state['user_id'] = user.user_id
    else:
        st.session_state['logged_in'] = False
else:
    st.session_state['logged_in'] = False

if "page" not in st.session_state:
    st.session_state['page'] = 'Main'

# Setup the UI
st.image("https://cultofthepartyparrot.com/parrots/hd/calvinist_parrot.gif",width=100)

if st.session_state['logged_in']:
    st.title(f"Welcome back to the Calvinist Parrot, {user.username}!")
else:
    st.title("Welcome to the Calvinist Parrot!")
st.write("I'm here to help you explore and understand the Bible through the lens of Reformed theology. Ask me any questions about the Scriptures, and I'll provide answers based on my knowledge and understanding.  \n\nI'm an AI-driven application. Using the 'Study Helper', I draw information from the [Bible Hub](https://biblehub.com/commentaries).")
st.write("ESV didn't let me use their API because they are not 'approving the pairing of the ESV text with AI-generated text.' Therefore, we use the Berean Standard Bible ([BSB](https://berean.bible/)) as our main translation. You can find more information about it [here](https://copy.church/initiatives/bibles/).")

st.divider()

st.write("""
👈 On the menu on the left, you can see all the tools you can use, like:
- **[Parrot](https://calvinistparrot.com/Parrot)**: You can chat with me here. I'll try to answer your questions based on my knowledge and understanding of the Bible from a Reformed perspective.
- **[CCEL](https://calvinistparrot.com/CCEL)**: You can search the [Christian Classics Ethereal Library](https://ccel.org) here. I'll try to find the best match for your query.
- **[Study Helper](https://calvinistparrot.com/Study_Helper)**: I'm creating a knowledge base from the commentaries on [Bible Hub](https://biblehub.com/commentaries). Ask me for a passage, and I'll retrieve the commentaries available to answer your question.
- **[Devotionals](https://calvinistparrot.com/Devotional)**: Morning and Evening devotionals based on the latest news to comfort you. Remember, AI generates these 😉.
- **[Sermon Review](https://calvinistparrot.com/Sermon_review)**: You can review sermons here. The evaluation based on Bryan Chappell's evaluation framework from his book, Christ-Centered Preaching.
""")

st.divider()

st.write("""
- Feb 2024 update: Due to lack of funding, I'm depricating the "Main Chat" since the cost to maintain the CCEL index is too high. I'm sorry for the inconvenience. I'll keep the "Study Helper" and "Devotionals" tools available. I'm also working on a new tool to help you study the Bible. Stay tuned!
- Mar 2024 update: New sermon review tool is up! You can now review sermons using Bryan Chappell's evaluation framework from his book, Christ-Centered Preaching.
- June 2024 update: The CCEL tool is back!

Fair warning: Session management is a bit wonky. I'm working on it. iOS doesn't play very well with sessions. I'm sorry for the inconvenience.
""")

st.markdown("I'm still learning, so please be patient with me! I'm always looking to improve, so if you have any feedback, <a href='mailto:jesus@jgmancilla.com'>please let me know</a>", unsafe_allow_html=True)
#   \n\nI'm also open source, so if you're interested in contributing to my development, check out my [GitHub](https://github.com/Jegama/calvinist-parrot)

# TODO: Add a link to the github repo