import streamlit as st
import ai_parrot.v1_brain as v1
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.EncryptedCookieManager_v2 import EncryptedCookieManager
from parrot_toolkit.sql_models import User, ConversationHistory
from PIL import Image
import google_connector as gc
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt
import os
from dotenv import load_dotenv
load_dotenv()

pool = gc.connect_with_connector('parrot_db')
SessionLocal = sessionmaker(bind=pool)

st.set_page_config(
    page_title="Calvinist Parrot v1", 
    page_icon="🦜",
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
    if user:
        st.session_state['logged_in'] = True
        st.session_state['username'] = user.username
        st.session_state['user_id'] = user.user_id
    else:
        st.session_state['logged_in'] = False
else:
    st.session_state['logged_in'] = False

from openai import OpenAI
client = OpenAI()

im = Image.open("app/calvin.ico")

def reset_status():
    st.session_state['new_conversation'] = True
    st.session_state["messages"] = [{"role": "parrot", "avatar": "🦜", "content": "What theological questions do you have?"}]
    st.session_state["parrot_conversation_history"] = [{"role": "system", "content": v1.parrot_sys_message}]
    st.session_state["calvin_conversation_history"] = [{"role": "system", "content": v1.calvin_sys_message}]

def update_status(msg):
    st.session_state["messages"].append(msg)
    if msg['role'] == "parrot":
        st.session_state["parrot_conversation_history"].append({"role": "system", "content": msg["content"]})
        st.session_state["calvin_conversation_history"].append({"role": "system", "content": f'/parrot/ {msg["content"]}'})
    else:
        st.session_state["parrot_conversation_history"].append({"role": "system", "content": f'/calvin/ {msg["content"]}'})
        st.session_state["calvin_conversation_history"].append({"role": "system", "content": msg["content"]})

def create_or_update_conversation(user_id, conversation_name, messages):
    db = SessionLocal()
    try:
        conversation = db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user.user_id, 
            ConversationHistory.conversation_name == conversation_name
        ).first()

        if conversation:
            conversation.messages = messages
            conversation.timestamp = dt.utcnow()
        else:
            new_conversation = ConversationHistory(
                user_id=user_id, 
                conversation_name=conversation_name, 
                messages=messages
            )
            db.add(new_conversation)
        db.commit()
    except Exception as e:
        print(f"Error updating or creating conversation: {e}")
    finally:
        db.close()

def interactWithAgents(question):
    st.session_state["parrot_conversation_history"].append({"role": "user", "content": f'/human/ {question}'})
    st.session_state["calvin_conversation_history"].append({"role": "user", "content": f'/human/ {question}'})
    
    with st.chat_message("parrot", avatar="🦜"):
        answer = ''
        c = st.empty()
        response = v1.get_response(st.session_state["parrot_conversation_history"], stream=True)
        for event in response:
            c.write(answer.split('/')[-1])
            event_text = event.choices[0].delta.content
            if event_text is not None:
                answer += event_text

    update_status({"role": "parrot", "content": answer.split('/')[-1]})

    with st.chat_message("calvin", avatar=im):
        answer = ''
        c = st.empty()
        response = v1.get_response(st.session_state["calvin_conversation_history"], stream=True)
        for event in response:
            c.write(answer.split('/')[-1])
            event_text = event.choices[0].delta.content
            if event_text is not None:
                answer += event_text

    update_status({"role": "calvin", "content": answer.split('/')[-1]})

    with st.chat_message("parrot", avatar="🦜"):
        answer = ''
        c = st.empty()
        response = v1.get_response(st.session_state["parrot_conversation_history"], stream=True)
        for event in response:
            c.write(answer.split('/')[-1])
            event_text = event.choices[0].delta.content
            if event_text is not None:
                answer += event_text

    update_status({"role": "parrot", "content": answer.split('/')[-1]})

    if st.session_state['new_conversation']:
        conversation_name = v1.generate_conversation_name(st.session_state["messages"])
        if conversation_name:
            st.session_state['new_conversation'] = False
            st.session_state['conversation_name'] = conversation_name
        
    # Save conversation history for logged-in users
    if st.session_state['logged_in']:
        db = SessionLocal()
        try:
            create_or_update_conversation(st.session_state['user_id'], st.session_state['conversation_name'], st.session_state["messages"])
        except Exception as e:
            st.error("Failed to save conversation history.")
            print("Error saving conversation history: ", e)
        finally:
            db.close()

def load_conversation_history(user_id):
    db = SessionLocal()
    try:
        conversations = db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id
        ).order_by(ConversationHistory.timestamp.desc()).all()
        
        if len(conversations) == 0:
            st.sidebar.write("No conversations yet. I'm looking forward to chatting with you!")
        else:
            for conversation in conversations:
                if st.sidebar.button(conversation.conversation_name):
                    # Load the selected conversation into st.session_state['messages']
                    st.session_state['messages'] = conversation.messages
                    st.session_state['new_conversation'] = False
                    st.session_state['conversation_name'] = conversation.conversation_name
                    st.rerun()
    except Exception as e:
        st.sidebar.error("Failed to load conversation history.")
        print("Error loading conversation history: ", e)
    finally:
        db.close()

def user_verification_setup(username, password, cookies):
    verify_user = auth.authenticate_user(username, password, cookies)
    if verify_user:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['user_id'] = verify_user.user_id
        st.success(f"Logged In as {username}")
        st.rerun()
    else:
        st.sidebar.warning("Incorrect Username/Password")

class main_parrot:
    def __init__(self):
        self.clear = st.sidebar.button("New Conversation")
        st.sidebar.divider()

        if st.session_state['logged_in']:
            st.sidebar.write(f"Logged in as {st.session_state['username']}")
            st.sidebar.subheader("Chat History")
            with st.container():
                load_conversation_history(st.session_state['user_id'])
            st.sidebar.divider()
            if st.sidebar.button('Logout'):
                st.session_state['logged_in'] = False
                auth.logout(cookies)
                st.success("You have been logged out.")
                reset_status()
                st.rerun()
        else:
            st.sidebar.write(f"Log in to see your chat history.")

            collapse_login = st.sidebar.checkbox("Login", key="login_collapse", value=False)
            if collapse_login:
                username = st.sidebar.text_input("Username", key="username_login")
                password = st.sidebar.text_input("Password", type='password', key="password_login")
                if st.sidebar.button("Login"):
                    user_verification_setup(username, password, cookies)
            
            collapse_register = st.sidebar.checkbox("Register", key="register_collapse", value=False)
            if collapse_register:
                username = st.sidebar.text_input("Username", key='username_register')
                st.sidebar.write('In the future, the parrot will use this name to refer to you.')
                name = st.sidebar.text_input("Name", key='name_register')
                password = st.sidebar.text_input("Password", type='password', key='password_register')
                if st.sidebar.button("Register"):
                    new_user = auth.create_user(username, password, name)
                    if new_user:
                        user_verification_setup(username, password, cookies)
                    else:
                        st.warning("Failed to create user.")

        # to show chat history on ui
        if "messages" not in st.session_state:
            reset_status()

    def main(self):
        if "page" not in st.session_state:
            st.session_state["page"] = "v1 Parrot"
        if st.session_state.page != "v1 Parrot":
            st.session_state["page"] = "v1 Parrot"
            reset_status()

        if self.clear:
            reset_status()

        for msg in st.session_state["messages"]:
            if msg["role"] == "parrot":
                avatar = "🦜"
            elif msg["role"] == "calvin":
                avatar = im
            else:
                avatar = "🧑‍💻"
            st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

        if prompt := st.chat_input(placeholder="What is predestination?"):
            st.chat_message("user", avatar="🧑‍💻").write(prompt)
            st.session_state.messages.append({"role": "user", "avatar": "🧑‍💻", "content": prompt})
            interactWithAgents(prompt)


if __name__ == "__main__":
    obj = main_parrot()
    obj.main()