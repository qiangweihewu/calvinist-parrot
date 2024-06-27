import streamlit as st
import parrot_toolkit.parrot_auth as auth
import ai_parrot.sermon_eval as se
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
    st.session_state['page'] = 'Sermon Review'
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
                st.session_state['sermon_title'] = None
                st.session_state['sermon_preacher'] = None
                st.session_state['review'] = None
                st.rerun()
        else:
            st.sidebar.write("Please log in to access your previous sermon reviews.")

        if "review" not in st.session_state:
            st.session_state['review'] = None

        if "sermon_title" not in st.session_state:
            st.session_state['sermon_title'] = None
        
        if "sermon_preacher" not in st.session_state:
            st.session_state['sermon_preacher'] = None

        if "yt_error" not in st.session_state:
            st.session_state['yt_error'] = False

    def main(self):
        if st.session_state['logged_in']:
            
            if st.session_state['review'] is not None and st.session_state['sermon_title'] is not None and st.session_state['sermon_preacher'] is not None:
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
                sermon_title = st.text_input("Enter the title of the sermon", key="sermon_title_field")
                sermon_preacher = st.text_input("Enter the preacher's name", key="sermon_preacher")
                if st.session_state['username'] in ['Jegama']:
                    disable_generate = True
                    st.write('You have access to the audio transcription tool!')
                    if st.checkbox("Use the audio transcription tool"):
                        if st.session_state['yt_error']:
                            st.warning("It looks like the link was for a YouTube Stream. I', sorry, but I can't transcribe those. Please upload the audio file instead.")
                            uploaded_file = st.file_uploader("MP3 file of the sermon", type=["mp3"], key="audio_file")
                            if uploaded_file is not None:
                                bytes_data = uploaded_file.read()
                                with open(uploaded_file.name, "wb") as f:
                                    f.write(bytes_data)
                                st.success("File uploaded successfully.")
                                st.write("Filename:", uploaded_file.name)
                        else:
                            youtube_link = st.text_input("Enter the YouTube link of the sermon", key="youtube_link")
                        if st.button("Generate Transcript"):
                            if not sermon_title or not sermon_preacher:
                                st.warning("Please provide the title and the preacher.")
                            else:
                                if st.session_state['yt_error']:
                                    with st.spinner("Splitting audio..."):
                                        snippets = se.split_audio(uploaded_file.name)
                                else:
                                    with st.spinner("Downloading audio..."):
                                        try:
                                            snippets = se.download_audio_pytube(youtube_link, sermon_title)
                                        except KeyError:
                                            st.warning(f"Failed to download audio, please upload the audio file instead.")
                                            st.session_state['yt_error'] = True
                                            st.rerun()
                                with st.spinner("Transcribing audio..."):
                                    review_text = se.create_and_append_transcripts(snippets, sermon_title)
                                if review_text:
                                    disable_generate = False
                                    st.success("Transcript generated successfully.")
                                    st.write("You can edit the transcript below if necessary. **Please download it** as the evaluation sometimes fails.\nIf that happens, **please use it** instead of re-doing the transcript.")
                                    st.download_button(
                                        "Download Transcript",
                                        review_text,
                                        f"{sermon_title} - Transcript.txt",
                                        "text/plain",
                                    )
                    else:
                        disable_generate = False
                        review_text = st.text_area("Enter the transcript of the sermon", key="review_text")
                else:
                    disable_generate = False
                    review_text = st.text_area("Enter the transcript of the sermon", key="review_text")
                if st.button("Generate Evaluation", disabled=disable_generate):
                    if not sermon_title or not sermon_preacher or not review_text:
                        st.warning("Please fill in all the fields.")
                    elif len(review_text.split()) < 1000:
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
                                first_eval = False
                    
                        if first_eval:
                            with st.spinner("Generating second section... This takes at least 60 seconds."):
                                second_eval = se.generate_eval_2(review_text, output)
                                review_markdown = se.convert_to_markdown_v2(second_eval, output)
                                if review_markdown:
                                    save_review_to_db(
                                        st.session_state['user_id'], 
                                        sermon_title, sermon_preacher, review_text, review_markdown
                                    )
                                    st.success("Second section generated successfully.")
                                    st.session_state['sermon_title'] = sermon_title
                                    st.session_state['sermon_preacher'] = sermon_preacher
                                    st.session_state['review'] = review_markdown
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
    obj = sermon_review()
    obj.main()