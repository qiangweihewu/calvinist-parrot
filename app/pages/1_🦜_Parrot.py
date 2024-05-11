import streamlit as st
import ai_parrot.v1_brain as v1
import parrot_toolkit.parrot_auth as auth
from parrot_toolkit.CookieManager import NEW_CM
from parrot_toolkit.sql_models import ConversationHistory
from PIL import Image
import google_connector as gc
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
load_dotenv()

pool = gc.connect_with_connector('parrot_db')
SessionLocal = sessionmaker(bind=pool)

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

st.set_page_config(
    page_title="Calvinist Parrot", 
    page_icon=parrot,
    layout="wide",
    menu_items={
        'Get help': 'https://svrbc.org/',
        'About': "v2.4\n\nCreated by: [Jesús Mancilla](mailto:jesus@jgmancilla.com)\n\nFrom [SVRBC](https://svrbc.org/)\n\n"
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
        st.session_state['human'] = user.name + ' - '
    else:
        st.session_state['logged_in'] = False
        st.session_state['human'] = '/human/'
else:
    st.session_state['logged_in'] = False
    st.session_state['human'] = '/human/'

from openai import OpenAI
client = OpenAI()

def reset_status():
    st.session_state['new_conversation'] = True
    st.session_state["messages"] = [{"role": "parrot", "content": "What theological questions do you have?"}]
    st.session_state["parrot_conversation_history"] = [{"role": "system", "content": v1.parrot_sys_message}]
    st.session_state["calvin_conversation_history"] = [{"role": "system", "content": v1.calvin_sys_message}]
    st.rerun()

def update_status(msg):
    st.session_state["messages"].append(msg)
    if msg['role'] == "parrot":
        st.session_state["parrot_conversation_history"].append({"role": "system", "content": msg["content"]})
        st.session_state["calvin_conversation_history"].append({"role": "system", "content": f'/parrot/ {msg["content"]} - What do you think, Calvin?'})
    else:
        st.session_state["parrot_conversation_history"].append({"role": "system", "content": f'/calvin/ {msg["content"]} - What do you think, Parrot?'})
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
            conversation.timestamp = dt.now(datetime.UTC)
        else:
            new_conversation = ConversationHistory(
                user_id=user_id, 
                conversation_name=conversation_name, 
                messages=messages
            )
            db.add(new_conversation)
        db.commit()
    except Exception as e:
        st.error(f"Error updating or creating conversation: {e}")
        print(f"Error updating or creating conversation: {e}")
    finally:
        db.close()

def interactWithAgents(question):
    st.session_state["parrot_conversation_history"].append({"role": "user", "content": f'{st.session_state["human"]} {question} - What do you think, Parrot?'})
    st.session_state["calvin_conversation_history"].append({"role": "user", "content": f'{st.session_state["human"]} {question}'})
    
    with st.chat_message("parrot", avatar=parrot):
        answer = ''
        c = st.empty()
        response = v1.get_response(st.session_state["parrot_conversation_history"], stream=True)
        for event in response:
            c.write(answer)
            event_text = event.choices[0].delta.content
            if event_text is not None:
                answer += event_text

    update_status({"role": "parrot", "content": answer})

    with st.chat_message("calvin", avatar=calvin):
        answer = ''
        c = st.empty()
        response = v1.get_response(st.session_state["calvin_conversation_history"], stream=True)
        for event in response:
            c.write(answer)
            event_text = event.choices[0].delta.content
            if event_text is not None:
                answer += event_text

    update_status({"role": "calvin", "content": answer})

    with st.chat_message("parrot", avatar=parrot):
        answer = ''
        c = st.empty()
        response = v1.get_response(st.session_state["parrot_conversation_history"], stream=True)
        for event in response:
            c.write(answer)
            event_text = event.choices[0].delta.content
            if event_text is not None:
                answer += event_text

    update_status({"role": "parrot", "content": answer})

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
            st.error(f"Failed to save conversation history: {e}")
            print("Error saving conversation history: ", e)
        finally:
            db.close()

def load_selected_conversation():
    for msg in st.session_state["messages"]:
        if msg["role"] == "parrot":
            st.session_state["parrot_conversation_history"].append({"role": "system", "content": msg["content"]})
            st.session_state["calvin_conversation_history"].append({"role": "system", "content": f'/parrot/ {msg["content"]} - What do you think, Calvin?'})
        elif msg["role"] == "calvin":
            st.session_state["parrot_conversation_history"].append({"role": "system", "content": f'/calvin/ {msg["content"]} - What do you think, Parrot?'})
            st.session_state["calvin_conversation_history"].append({"role": "system", "content": msg["content"]})
        else:
            st.session_state["parrot_conversation_history"].append({"role": "user", "content": f'{st.session_state["human"]} {msg["content"]} - What do you think, Parrot?'})
            st.session_state["calvin_conversation_history"].append({"role": "user", "content": f'{st.session_state["human"]} {msg["content"]}'})

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
                    load_selected_conversation()
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
        st.warning("Incorrect Username/Password")

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
                cookie_manager.delete_cookie()
                st.success("You have been logged out.")
                reset_status()
                st.rerun()
        else:
            st.sidebar.write(f"Please log in to see your chat history.")

        # to show chat history on ui
        if "messages" not in st.session_state:
            reset_status()

    def main(self):
        if st.session_state['logged_in']:
            st.write(f"You are logged in as {st.session_state['username']}.")
            for msg in st.session_state["messages"]:
                if msg["role"] == "parrot":
                    avatar = parrot
                elif msg["role"] == "calvin":
                    avatar = calvin
                else:
                    avatar = "🧑‍💻"
                st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

            if prompt := st.chat_input(placeholder="What is predestination?"):
                st.chat_message("user", avatar="🧑‍💻").write(prompt)
                st.session_state.messages.append({"role": "user", "avatar": "🧑‍💻", "content": prompt})
                interactWithAgents(prompt)
        else:
            st.title("Welcome to the Calvinist Parrot!")
            st.write("To take full advantage of the Calvinist Parrot, please log in. If you don't have an account, you can register for free.")
            username = st.text_input("Username", key="username_login")
            password = st.text_input("Password", type='password', key="password_login")
            if st.button("Login"):
                user_verification_setup(username, password, cookie_manager)

            if st.checkbox("New User? Register here."):
                username = st.text_input("Username", key='username_register')
                st.write('In the future, the parrot will use this name to refer to you.')
                name = st.text_input("Name", key='name_register')
                password = st.text_input("Password", type='password', key='password_register')
                if st.button("Register"):
                    new_user = auth.create_user(username, password, name)
                    if new_user:
                        user_verification_setup(username, password, cookie_manager)
                    else:
                        st.warning("Failed to create user.")


        if "page" not in st.session_state:
            st.session_state["page"] = "v1 Parrot"
        if st.session_state.page != "v1 Parrot":
            st.session_state["page"] = "v1 Parrot"
            reset_status()

        if self.clear:
            reset_status()

if __name__ == "__main__":
    obj = main_parrot()
    obj.main()