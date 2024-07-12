import streamlit as st
import parrot_toolkit.parrot_auth as auth
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

if 'cookie_name' not in st.session_state:
    st.session_state['cookie_name'] = ""

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login(st.session_state['cookie_name'])

st.session_state['url'] = os.environ.get('URL')

# Setting up the language
if 'language' not in st.session_state:
    if st.session_state['logged_in'] == False:
        if st.session_state['url'] == 'loro':
            st.session_state['language'] = 'Español'
        else:
            st.session_state['language'] = 'English'

if st.session_state['language'] in ['Español', 'Spanish']:
    from parrot_toolkit.spanish_text import *
else:
    from parrot_toolkit.english_text import *

def homepage():
    st.image("https://cultofthepartyparrot.com/parrots/hd/calvinist_parrot.gif",width=100)

    st.title(HOME_TITLE)
        
    st.write(HOME_INTRO)

    st.divider()

    st.write(HOME_MENU_INTRO)

    st.divider()

    st.markdown(HOME_FOOTER, unsafe_allow_html=True)


home = st.Page(homepage, title=f"{pages[0]} v2.7", icon="🦜")

login_page = st.Page("directory/parrot_login.py", title=pages[5], icon=":material/login:")
register_page = st.Page("directory/parrot_register.py", title=pages[6], icon=":material/assignment_ind:")
logout_page = st.Page(auth.logout, title=pages[7], icon=":material/logout:")

v2_parrot = st.Page("directory/Parrot.py", title=pages[0], icon="🦜")
ccel_page = st.Page("directory/CCEL.py", title="CCEL", icon="📚")
study_helper = st.Page("directory/Study_Helper.py", title=pages[1], icon="📖")
devotionals = st.Page("directory/Devotional.py", title=pages[2], icon="📜")
sermon_review = st.Page("directory/Sermon_review.py", title=pages[3], icon="👨‍🏫")
bible_studies = st.Page("directory/Bible_studies.py", title=pages[4], icon="✒️")
nav_tools_eng = [ccel_page, study_helper, sermon_review]
nav_tools_esp = [ccel_page, study_helper]
nav_tools_jegama = [ccel_page, study_helper, sermon_review, bible_studies]

if st.session_state['language'] in ['Español', 'Spanish']:
    nav_tools = nav_tools_esp
else:
    nav_tools = nav_tools_jegama if st.session_state['username'] == 'Jegama' else nav_tools_eng


if st.session_state['logged_in']:
    pg = st.navigation(
        {
            "Main": [v2_parrot, devotionals],
            "Tools": nav_tools,
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