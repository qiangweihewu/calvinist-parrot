import streamlit as st
import parrot_toolkit.parrot_auth as auth
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

# st.set_page_config(
#     page_title="Calvinist Parrot v2.5",
#     page_icon=parrot,
#     layout="wide",
#     menu_items={
#         'Get help': 'https://svrbc.org/',
#         'About': "v2.5\n\nCreated by: [Jesús Mancilla](mailto:jesus@jgmancilla.com)\n\nFrom [SVRBC](https://svrbc.org/)\n\n"
#     }
# )

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login()

def homepage():
    st.image("https://cultofthepartyparrot.com/parrots/hd/calvinist_parrot.gif",width=100)

    if st.session_state['logged_in']:
        st.title(f"Welcome back to the Calvinist Parrot, {st.session_state['username']}!")
    else:
        st.title("Welcome to the Calvinist Parrot!")
        
    st.write("Welcome! I'm here to guide you through the Bible from a Reformed perspective. Feel free to ask me anything about Scripture, and I'll provide insights based on my knowledge and understanding as a Reformed Baptist.\n\nAs an AI-driven application, I provide with multiple tools that gather information from sources like the [Christian Classics Ethereal Library](https://ccel.org) and [Bible Hub](https://biblehub.com/commentaries) to enhance your time in the Bible.")
    
    st.write("While I can't use the ESV due to restrictions, we rely on the Berean Standard Bible ([BSB](https://berean.bible/)) for our primary translation. Learn more about the BSB [here](https://copy.church/initiatives/bibles/) and join us in discovering the richness of its text.")

    st.divider()

    st.write("""\
             Explore the tools available on the left menu:

- **Calvinist Parrot**: Engage in discussions and questions from a Reformed perspective on the Bible. Parrot, Calvin, and a CCEL Librarian are here to help you learn and grow in your understanding of Scripture.
- **CCEL**: Dive into the treasures of the [Christian Classics Ethereal Library](https://ccel.org) for timeless Christian writings.
- **Study Helper**: Access commentaries from [Bible Hub](https://biblehub.com/commentaries) to enrich your study of Scripture.
- **Devotionals**: Start or end your day with AI-generated morning and evening reflections for comfort and inspiration.
- **Sermon Review**: Evaluate your sermons using Bryan Chappell's Christ-Centered Preaching framework.\
             """)

    st.divider()

    st.write("""
    - Feb 2024 update: Due to lack of funding, I'm depricating the "Main Chat" since the cost to maintain the CCEL index is too high. I'm sorry for the inconvenience. I'll keep the "Study Helper" and "Devotionals" tools available. I'm also working on a new tool to help you study the Bible. Stay tuned!
    - Mar 2024 update: New sermon review tool is up! You can now review sermons using Bryan Chappell's evaluation framework from his book, Christ-Centered Preaching.
    - June 2024 update: The CCEL tool is back!

    Fair warning: Session management is a bit wonky. I'm working on it. iOS doesn't play very well with sessions. I'm sorry for the inconvenience.
    """)

    st.markdown("I'm still learning, so please be patient with me! I'm always looking to improve, so if you have any feedback, <a href='mailto:jesus@jgmancilla.com'>please let me know</a> \n\nI'm also open source, so if you're interested in contributing to my development, check out my [GitHub](https://github.com/Jegama/calvinist-parrot)", unsafe_allow_html=True)


home = st.Page(homepage, title="Calvinist Parrot v2.6", icon="🦜")

login_page = st.Page("directory/parrot_login.py", title="Log in", icon=":material/login:")
register_page = st.Page("directory/parrot_register.py", title="Register", icon=":material/assignment_ind:")
logout_page = st.Page(auth.logout, title="Log out", icon=":material/logout:")

v2_parrot = st.Page("directory/Parrot.py", title="Calvinist Parrot", icon="🦜")
ccel_page = st.Page("directory/CCEL.py", title="CCEL", icon="📚")
study_helper = st.Page("directory/Study_Helper.py", title="Study Helper", icon="📖")
devotionals = st.Page("directory/Devotional.py", title="Devotionals", icon="📜")
sermon_review = st.Page("directory/Sermon_review.py", title="Sermon Review", icon="👨‍🏫")
bible_studies = st.Page("directory/Bible_studies.py", title="Bible Studies", icon="✒️")
nav_tools = [ccel_page, study_helper, sermon_review]
nav_tools_extended = [ccel_page, study_helper, sermon_review, bible_studies]


if st.session_state['logged_in']:
    pg = st.navigation(
        {
            "Main": [v2_parrot, devotionals],
            "Tools": nav_tools_extended if st.session_state['username'] == 'Jegama' else nav_tools,
            "Account": [logout_page],
        }
    )
else:
    pg = st.navigation(
        {
            "Main": [home, login_page, register_page],
            "Tools": [ccel_page, study_helper],
            "Other": [devotionals]
        }
    )

pg.run()