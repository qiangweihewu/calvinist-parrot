import streamlit as st
import parrot_toolkit.parrot_auth as auth

st.title("Welcome to the Calvinist Parrot!")
st.write("To take full advantage of the Calvinist Parrot, please log in. If you don't have an account, you can register for free.")
username = st.text_input("Username", key="username_login")
password = st.text_input("Password", type='password', key="password_login")
if st.button("Log in"):
    auth.user_verification(username, password)