import streamlit as st
import parrot_toolkit.parrot_auth as auth
import parrot_toolkit.sermon_eval as se
from parrot_toolkit.CookieManager import NEW_CM
from parrot_toolkit.sql_models import SermonReview, SessionLocal
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()

im = Image.open("app/calvinist_parrot.ico")

st.set_page_config(
    page_title="Sermon Review", 
    page_icon="👨‍🏫",
    layout="wide",
    menu_items={
        'Get help': 'https://svrbc.org/',
        'About': "v2.3\n\nCreated by: [Jesús Mancilla](mailto:jesus@jgmancilla.com)\n\nFrom [SVRBC](https://svrbc.org/)\n\n"
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
    st.session_state['page'] = 'Sermon Review'

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

def save_review_to_db(user_id, sermon_title, preacher, transcript, review):
    db = SessionLocal()
    new_review = SermonReview(
        user_id=user_id, 
        sermon_title=sermon_title, 
        preacher=preacher, 
        transcript=transcript, 
        review_markdown=review
    )
    db.add(new_review)
    db.commit()
    db.close()

def load_previous_reviews(user_id):
    db = SessionLocal()
    try:
        reviews = db.query(SermonReview).filter(
            SermonReview.user_id == user_id
        ).order_by(SermonReview.timestamp.desc()).all()
        db.close()

        if len(reviews) == 0:
            st.sidebar.write("You haven't reviewed any sermons yet.")
        else:
            for review in reviews:
                if st.sidebar.button(review.sermon_title):
                    st.session_state['sermon_title'] = review.sermon_title
                    st.session_state['sermon_preacher'] = review.preacher
                    st.session_state['review'] = review.review_markdown
                    st.rerun()
    except Exception as e:
        st.sidebar.error(f"An unexpected error occurred while loading the previous reviews: {e}")
    finally:
        db.close()

# Setup the UI
class sermon_review:
    def __init__(self):
        if st.session_state['logged_in']:
            st.sidebar.write(f"Logged in as {st.session_state['username']}")
            st.sidebar.subheader("Your Previous Sermon Reviews")
            with st.container():
                load_previous_reviews(st.session_state['user_id'])
            st.sidebar.divider()
            if st.sidebar.button('Logout'):
                st.session_state['logged_in'] = False
                cookie_manager.delete_cookie()
                st.success("You have been logged out.")
                st.session_state['review'] = None
                st.rerun()
        else:
            st.sidebar.write("Please log in to access your previous sermon reviews.")

        if "review" not in st.session_state:
            st.session_state['review'] = None

    def main(self):
        if st.session_state['logged_in']:
            
            if st.session_state['review']:
                if st.button("New Review"):
                    st.session_state['sermon_title'] = None
                    st.session_state['sermon_preacher'] = None
                    st.session_state['review'] = None
                    st.rerun()

                st.header(st.session_state['sermon_title'])
                st.write(f"Preacher: {st.session_state['sermon_preacher']}")
                st.markdown(st.session_state['review'])
                st.divider()
                output_file = f"{st.session_state['sermon_preacher']} - {st.session_state['sermon_title']} - Sermon Review.md"
                st.download_button(
                    'Download Review', 
                    st.session_state['review'], 
                    file_name=output_file, 
                    mime='text/markdown'
                )
            else:
                st.header("What sermon would you like to review today?")
                st.write("The Calvinist Parrot uses Bryan Chappell's evaluation framework from his book, Christ-Centered Preaching, to evaluate sermons.")
                output = ""
                sermon_title = st.text_input("Enter the title of the sermon", key="sermon_title")
                sermon_preacher = st.text_input("Enter the preacher's name", key="sermon_preacher")
                review_text = st.text_area("Enter the transcript of the sermon", key="review_input")
                if st.button("Generate Evaluation"):
                    if not sermon_title or not sermon_preacher or not review_text:
                        st.warning("Please fill in all the fields.")
                    elif len(review_text.split()) < 100:
                        st.warning("The transcript is too short. Are you sure this is the full sermon?")
                    else:
                        with st.spinner("Generating first section... This takes at least 60 seconds."):
                            first_eval = se.generate_eval(review_text)
                            if first_eval:
                                try:
                                    output, confidence_score = se.first_eval_to_markdown(first_eval)
                                    st.success("First section generated successfully.")
                                except:
                                    st.warning("Failed to generate evaluation.")
                                    first_eval = False
                            else:
                                st.warning("Failed to generate evaluation.")
                    
                        if first_eval:
                            with st.spinner("Generating second section... This takes at least 60 seconds."):
                                second_eval = se.generate_eval_2(review_text, output)
                                if second_eval:
                                    st.session_state['review'] = se.convert_to_markdown_v2(second_eval, output)
                                    save_review_to_db(
                                        st.session_state['user_id'],
                                        sermon_title, sermon_preacher, review_text, output
                                        )
                                    output_file = 'eval_' + sermon_title.lower().replace(' ', '_') + '.md'
                                    st.success("Second section generated successfully.")
                                    st.rerun()
                                else:
                                    st.warning("Failed to generate Second section.")

        else:
            st.title("Welcome to the Calvinist Parrot!")
            st.write("To take full advantage of the Calvinist Parrot, please log in. If you don't have an account, you can register for free.")
            username = st.text_input("Username", key="username_login")
            password = st.text_input("Password", type='password', key="password_login")
            if st.button("Login"):
                user_verification_setup(username, password, cookie_manager)

            with st.expander("Register"):
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


if __name__ == "__main__":
    obj = sermon_review()
    obj.main()