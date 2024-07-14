import streamlit as st
import parrot_toolkit.parrot_auth as auth
import parrot_ai.study_generator as sg
from PIL import Image

parrot = Image.open("app/calvinist_parrot.ico")
calvin = Image.open("app/calvin.ico")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    auth.check_login()

if "page" not in st.session_state:
    st.session_state['page'] = 'Bible Study Generator'
    st.session_state['review'] = None

def load_previous_studies(user_id):
    studies = sg.get_studies(user_id)
    if len(studies) == 0:
        st.sidebar.write("You don't have any studies yet.")
    else:
        for idx, study in enumerate(studies):
            if st.sidebar.button(study.title, key=f"study_button_{idx}"):
                st.session_state['title'] = study.title
                st.session_state['bible_verse'] = study.bible_verse
                st.session_state['biblie_study'] = study.bible_study_text
                st.session_state['audience'] = study.audience
                st.rerun()

if st.session_state['logged_in']:
    st.sidebar.write(f"Logged in as {st.session_state['username']}")
    st.sidebar.subheader("Your Previous Bible Studies")
    with st.container():
        load_previous_studies(st.session_state['user_id'])
else:
    st.sidebar.write("Please log in to access your previous Bible studies.")

if "title" not in st.session_state:
    st.session_state['title'] = None
    st.session_state['bible_verse'] = None
    st.session_state['biblie_study'] = None
    st.session_state['audience'] = None

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
            st.image("https://cultofthepartyparrot.com/parrots/hd/calvinist_parrot.gif",width=100)
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
                    sg.save_study_to_db(
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