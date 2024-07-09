import streamlit as st
import parrot_toolkit.parrot_auth as auth
import parrot_ai.sermon_eval as se
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

im = Image.open("app/calvinist_parrot.ico")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login()

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

# Setting up the session state
for key in ['sermon_title', 'sermon_preacher', 'sermon_text', 'review']:
    if key not in st.session_state:
        st.session_state[key] = ""

if "page" not in st.session_state:
    st.session_state['page'] = pages[3]

def load_previous_reviews(user_id):
    reviews = se.get_reviews(user_id)

    if len(reviews) == 0:
        st.sidebar.write(SR_SIDE_NO_REVIEWS)
    else:
        for idx, review in enumerate(reviews):
            if st.sidebar.button(review.sermon_title, key=f"review_button_{idx}"):
                st.session_state['sermon_title'] = review.sermon_title
                st.session_state['sermon_preacher'] = review.preacher
                st.session_state['review'] = review.review_markdown
                st.rerun()

if st.session_state['logged_in']:
    st.sidebar.write(f"{LOGGED_AS} {st.session_state['username']}")
    st.sidebar.subheader("Your Previous Sermon Reviews")
    with st.container():
        load_previous_reviews(st.session_state['user_id'])
else:
    st.sidebar.write("Please log in to access your previous sermon reviews.")

# Main content
if st.session_state['logged_in']:

    # If a review is already loaded
    if st.session_state['review'] != "":

        # Button to start a new review
        if st.button(SR_SIDE_NEW_REVIEW):
            st.session_state['sermon_title'] = ""
            st.session_state['sermon_preacher'] = ""
            st.session_state['review'] = ""
            st.session_state['sermon_text'] = ""
            st.rerun()

        # Display the review
        st.header(st.session_state['sermon_title'])
        st.write(f"Preacher: {st.session_state['sermon_preacher']}")
        st.markdown(st.session_state['review'])
        st.divider()

        # Download button
        output_file = f"{st.session_state['sermon_preacher']} - {st.session_state['sermon_title']} - Sermon Review.md"
        st.download_button(
            SR_DOWNLOAD_REVIEW, 
            st.session_state['review'], 
            file_name=output_file, 
            mime='text/markdown'
        )
    else:
        # Fix for button error
        if st.session_state['sermon_text'] != "":
            # Generate the evaluation functions see parrot_ai/sermon_eval.py
            with st.spinner(SR_SPINNER_1):
                first_eval = se.generate_eval(st.session_state['sermon_text'])
                # If the evaluation is generated, convert it to markdown
                if first_eval:
                    try:
                        output, confidence_score = se.first_eval_to_markdown(first_eval)
                        st.success(SR_1_SUCCESS)
                    except:
                        st.warning(SR_1_FAIL)
                        first_eval = False
                else:
                    st.warning(SR_1_FAIL)
                    first_eval = False
                    # TODO: Add a way to save the transcript and try again

            if first_eval:
                with st.spinner(SR_SPINNER_2):
                    second_eval = se.generate_eval_2(st.session_state['sermon_text'], output)
                    review_markdown = se.convert_to_markdown_v2(second_eval, output)
                    if review_markdown:
                        se.save_review_to_db(
                            st.session_state['user_id'], 
                            st.session_state['sermon_title'], st.session_state['sermon_preacher'], st.session_state['sermon_text'], review_markdown
                        )
                        st.success(SR_2_SUCCESS)
                        st.session_state['review'] = review_markdown
                        st.rerun()
                    else:
                        st.warning(SR_2_FAIL)
                        #TODO: Add a way to save the transcript and try again
            # else:
                # TODO: What fall back should be here?

        # New review
        st.header(SR_NEW_REVIEW_HEADER)
        st.write(SR_NEW_REVIEW_INTRO)
        output = ""
        sermon_title = st.text_input(SR_SERMON_TITLE, value=st.session_state['sermon_title'], key="sermon_title_field")
        sermon_preacher = st.text_input(SR_PREACHER, value=st.session_state['sermon_preacher'], key="sermon_preacher_field")
        sermon_text = st.text_area(SR_TRANSCRIPT, value=st.session_state['sermon_text'], key="sermon_text_filed")

        # Update session state with the input values
        st.session_state['sermon_title'] = sermon_title
        st.session_state['sermon_preacher'] = sermon_preacher
        st.session_state['sermon_text'] = sermon_text

        # Generate the evaluation
        if st.button(SR_GENERATE_BUTTON):
            # Check if the fields are filled
            if not sermon_title or not sermon_preacher or not sermon_text:
                st.warning(SR_NOT_ALL_FIELDS)
            elif len(sermon_text.split()) < 1000: # Check if the transcript is too short
                st.warning(SR_TRANSCRIPT_TOO_SHORT)
            else:
                st.rerun()