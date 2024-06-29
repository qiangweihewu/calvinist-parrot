import streamlit as st
import parrot_toolkit.parrot_auth as auth

st.title("Welcome to the Calvinist Parrot!")
st.write("To take full advantage of the Calvinist Parrot, please log in. If you don't have an account, you can register for free.")
username = st.text_input("Username", key="username_login")
password = st.text_input("Password", type='password', key="password_login")
if st.button("Log in"):
    auth.user_verification(username, password)

if st.checkbox("New User? Register here."):
    username = st.text_input("Username", key='username_register')
    st.write('The parrot will use this name to refer to you.')
    name = st.text_input("Name", key='name_register')
    password = st.text_input("Password", type='password', key='password_register')
    if st.button("Register"):
        new_user = auth.create_user(username, password, name)
        if new_user:
            auth.user_verification(username, password)
        else:
            st.warning("Failed to create user.")