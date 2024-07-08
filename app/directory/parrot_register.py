import streamlit as st
import parrot_toolkit.parrot_auth as auth

# Setting up the language
if 'language' not in st.session_state:
    if st.session_state['logged_in'] == False:
        if 'loro' in str(st.session_state['url']):
            st.session_state['language'] = 'Español'
        else:
            st.session_state['language'] = 'English'

if st.session_state['language'] in ['Español', 'Spanish']:
    from parrot_toolkit.spanish_text import *
else:
    from parrot_toolkit.english_text import *

st.title(HOME_TITLE)
st.write(REGISTER_WELCOME)

username = st.text_input(LOGIN_USERNAME, key='username_register', placeholder=REGISTER_USERNAME_PLACEHOLDER)
name = st.text_input(REGISTER_NAME, placeholder=REGISTER_NAME_PLACEHOLDER, key='name_register', help=REGISTER_NAME_HELP)
password = st.text_input(LOGIN_PASSWORD, type='password', key='password_register', help=REGISTER_PASSWORD_HELP)
language = st.selectbox(REGISTER_LANGUAGE, languages, key='language_register')

if st.button(REGISTER_BUTTON):
    new_user = auth.create_user(username, password, name, language)
    if new_user:
        auth.user_verification(username, password)
    else:
        st.warning(ERROR_CREATE_USER)