import streamlit as st
import parrot_toolkit.parrot_auth as auth

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

st.title(HOME_TITLE)
st.write(LOGIN_WELCOME)
username = st.text_input(LOGIN_USERNAME, key="username_login")
password = st.text_input(LOGIN_PASSWORD, type='password', key="password_login")
if st.button(LOGIN_BUTTON):
    auth.user_verification(username, password)