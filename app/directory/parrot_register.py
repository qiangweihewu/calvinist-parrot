import streamlit as st
import parrot_toolkit.parrot_auth as auth

st.title("Welcome to the Calvinist Parrot!")
st.write("To take full advantage of the Calvinist Parrot, please create an account, you can register for free.")

username = st.text_input("Username", key='username_register', placeholder='This will be your login name.')
name = st.text_input("Name", placeholder="John Doe", key='name_register', help='The parrot will use this name to refer to you.')
password = st.text_input("Password", type='password', key='password_register', help='Please use a strong password.')

if st.button("Register"):
    new_user = auth.create_user(username, password, name)
    if new_user:
        auth.user_verification(username, password)
    else:
        st.warning("Failed to create user.")