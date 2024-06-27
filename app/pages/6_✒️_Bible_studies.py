import streamlit as st
import parrot_toolkit.parrot_auth as auth
import ai_parrot.study_generator as sg
from parrot_toolkit.CookieManager import NEW_CM
from parrot_toolkit.sql_models import BibleStudies, SessionLocal
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

st.set_page_config(
    page_title="Bible Study Generator", 
    page_icon="✒️",
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
    st.session_state['page'] = 'Bible Study Generator'
    st.session_state['review'] = None

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

def save_review_to_db(user_id, title, bible_verse, topic, audience, bible_study_text):
    db = SessionLocal()
    new_study = BibleStudies(
        user_id=user_id,
        title=title,
        bible_verse=bible_verse,
        topic=topic,
        audience=audience,
        bible_study_text=bible_study_text
    )
    db.add(new_study)
    db.commit()
    db.close()

def load_previous_study(user_id):
    db = SessionLocal()
    studies = db.query(BibleStudies).filter(BibleStudies.user_id == user_id).all()
    try:
        studies = db.query(BibleStudies).filter(
            BibleStudies.user_id == user_id
        ).order_by(BibleStudies.timestamp.desc()).all()
        db.close()

        if len(studies) == 0:
            st.sidebar.write("You haven't reviewed any sermons yet.")
        else:
            for study in studies:
                if st.sidebar.button(study.title):
                    st.session_state['title'] = study.title
                    st.session_state['bible_verse'] = study.bible_verse
                    st.session_state['biblie_study'] = study.bible_study_text
                    st.session_state['audience'] = study.audience
                    st.rerun()
    except Exception as e:
        st.sidebar.error(f"An unexpected error occurred while loading the previous reviews: {e}")
    finally:
        db.close()
    db.close()

# Setup UI
class bible_study_generator:
    def __init__(self):
        if st.session_state['logged_in']:
            st.sidebar.write(f"Logged in as {st.session_state['username']}")
            st.sidebar.subheader("Your Previous Bible Studies")
            with st.container():
                load_previous_study(st.session_state['user_id'])
            st.sidebar.divider()
            if st.sidebar.button('Logout'):
                st.session_state['logged_in'] = False
                cookie_manager.delete_cookie()
                st.success("You have been logged out.")
                st.session_state['title'] = None
                st.session_state['bible_verse'] = None
                st.session_state['biblie_study'] = None
                st.session_state['audience'] = None
                st.rerun()
        else:
            st.sidebar.write("Please log in to access your previous Bible studies.")
        
        if "title" not in st.session_state:
            st.session_state['title'] = None
            st.session_state['bible_verse'] = None
            st.session_state['biblie_study'] = None
            st.session_state['audience'] = None
    
    def main(self):
        if st.session_state['logged_in']:
            
            if st.session_state['title'] is not None:
                col1, col2 = st.columns([.8,.2])
                with col1:
                    if st.button("New Bible Study"):
                        st.session_state['title'] = None
                        st.session_state['bible_verse'] = None
                        st.session_state['biblie_study'] = None
                        st.session_state['audience'] = None
                        st.rerun()
                    st.write(f"Passage: {st.session_state['bible_verse']}")
                    st.write(f'Intended Audience: {st.session_state["audience"]}')
                with col2:
                    st.image(parrot, width=100)
                st.divider()
                st.markdown(st.session_state['biblie_study'])
                st.divider()
                output_file = f"{st.session_state['bible_verse']} - {st.session_state['title']} - Bible Study.md"
                st.download_button(
                    'Download Bible Study', 
                    st.session_state['biblie_study'], 
                    file_name=output_file, 
                    mime='text/markdown'
                )
            else:                
                if st.session_state['username'] in ['Jegama']:
                    reference = st.text_input("What will be the core passage?", key="reference")
                    if reference:
                        try:
                            passage, reference_db = sg.get_text(reference)
                            st.write(passage)
                        except UnboundLocalError:
                            st.error("Invalid reference. Please try again.")
                    desired_topic = st.text_input("What is the desired topic?", key="desired_topic")
                    audience = st.selectbox(
                        "Who would be the audience of this Bible Study?",
                        ("Elementary School Kids", "Elementary School Boys", "Element School Girls", "Middle School Kids", "Middle School Boys", "Middle School Girls", "High School Students", "High School Boys", "High School Girls", "College Students", "College Student Men", "College Student Women", "Young Adults", "Young Men", "Young Women", "Adults", "Adult Men", "Adult Women", "Seniors", "Senior Men", "Senior Women"),
                        index=None,
                        placeholder="Select your audience..."
                    )
                    if st.button("Generate Bible Study"):
                        if not desired_topic or not audience:
                            st.warning("Please provide the topic and the audience.")
                        else:
                            with st.spinner("Parrot is writting first draft... This takes about 30 seconds."):
                                draft = sg.generate_draft(passage, reference, desired_topic, audience)
                            st.success("Draft generated successfully.")
                            with st.expander("Draft"):
                                st.image(parrot, width=100)
                                st.write(draft)
                            with st.spinner("Calvin is reviewing the draft... This takes about 30 seconds."):
                                review = sg.generate_review(draft, reference, desired_topic, audience)
                            st.success("Review generated successfully.")
                            with st.expander("Review"):
                                st.image(calvin, width=100)
                                st.write(review)
                            with st.spinner("Parrot is writing a revised version of the study... This takes about 30 seconds"):
                                final_study = sg.generate_final_study(passage, reference, desired_topic, audience, draft, review)
                            st.success("Final study generated successfully.")
                            save_review_to_db(
                                st.session_state['user_id'], 
                                final_study.split('\n\n')[0], reference_db, desired_topic, audience, final_study
                            )
                            st.session_state['title'] = final_study.split('\n\n')[0]
                            st.session_state['bible_verse'] = reference_db
                            st.session_state['biblie_study'] = final_study
                            st.rerun()
                else:
                    st.header("AI Bible Study Generation")
                    st.write("This feature is currently in close beta. If you would like to participate, please reach out to [Jesús Mancilla](mailto:jesus@jgmancilla.com) telling me a bit about you and why you would like to use this tool and what is your target audience. Please include your username.")

        else:
            st.title("Welcome to the Calvinist Parrot!")
            st.write("To take full advantage of the Calvinist Parrot, please log in. If you don't have an account, you can register for free.")
            username = st.text_input("Username", key="username_login")
            password = st.text_input("Password", type='password', key="password_login")
            if st.button("Login"):
                user_verification_setup(username, password, cookie_manager)
            if st.checkbox("New User? Register here."):
                username = st.text_input("Username", key='username_register')
                name = st.text_input("Name", key='name_register')
                password = st.text_input("Password", type='password', key='password_register')
                if st.button("Register"):
                    new_user = auth.create_user(username, password, name)
                    if new_user:
                        user_verification_setup(username, password, cookie_manager)
                    else:
                        st.warning("Failed to create user.")


if __name__ == "__main__":
    obj = bible_study_generator()
    obj.main()