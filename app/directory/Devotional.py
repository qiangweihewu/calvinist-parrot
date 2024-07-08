import streamlit as st
from dotenv import load_dotenv
import parrot_ai.devotional as dtk
from datetime import datetime as dt
import pytz
et = pytz.timezone('US/Eastern')

load_dotenv()

# Setting up the language
now_ = dt.now(et)

# Setting up the language
if 'language' not in st.session_state:
    if st.session_state['logged_in'] == False:
        if 'loro' in str(st.session_state['url']):
            st.session_state['language'] = 'Español'
        else:
            st.session_state['language'] = 'English'

if st.session_state['language'] in ['Español', 'Spanish']:
    from parrot_toolkit.spanish_text import *
else:
    from parrot_toolkit.english_text import *

devotional_type = "evening" if now_.hour >= 17 or now_.hour < 5 else "morning"
id_ = now_.strftime("%Y_%m_%d")
id_ += f"_{devotional_type}_devotional_{st.session_state['language']}"

if "devotional" not in st.session_state:
    devotional = dtk.check_if_devotional_exists(id_)
    if devotional is not None:
        st.session_state["devotional"] = devotional
    else:
        with st.spinner(DEVOTIONALS_SPINNER):
            dtk.generate_devotional()
            st.session_state["devotional"] = dtk.check_if_devotional_exists(id_)

if "page" not in st.session_state:
    st.session_state["page"] = pages[2]
if st.session_state["page"] != pages[2]:
    st.session_state["page"] = pages[2]

st.header(f"Devotional for {now_.strftime('%A, %B %d, %Y')}")
st.subheader(st.session_state.devotional.title)
if st.session_state['language'] in ['Español', 'Spanish']:
    temp = "Devocional Vespertino" if now_.hour >= 17 or now_.hour < 5 else "Devocional Matutino"
    st.write(temp)
else:
    st.write(f"{devotional_type.capitalize()} devotional")
st.divider()
st.write(dtk.get_text(st.session_state.devotional.bible_verse))
st.divider()
st.write(st.session_state.devotional.devotional_text)
st.divider()
st.write(DEVOTIONALS_FOOTER)
with st.expander(DEVOTIONALS_EXPANDER):
    st.write(DEVOTIONALS_EXPANDER_TITLE)
    st.write(" - " + st.session_state.devotional.news_articles)