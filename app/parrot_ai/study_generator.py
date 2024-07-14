import streamlit as st
from parrot_toolkit.sql_models import BibleStudies, SessionLocal
from parrot_ai.core.prompts import STUDY_GEN_SYS_PROMPT, CALVIN_SYS_PROMPT
import os

gpt_model = os.environ.get("GPT_MODEL")

def save_study_to_db(user_id, title, bible_verse, topic, audience, bible_study_text):
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

def get_studies(user_id):
    db = SessionLocal()
    try:
        studies = db.query(BibleStudies).filter(
            BibleStudies.user_id == user_id
        ).order_by(BibleStudies.timestamp.desc()).all()
        db.close()
    except Exception as e:
        st.sidebar.error(f"An unexpected error occurred while loading the previous reviews: {e}")
        studies = []
    finally:
        db.close()
        
    return studies

from openai import OpenAI
client = OpenAI()

def generate_first_message(passage, reference, desired_topic, audience):
    message = f"""You are writing a Bible study for your congregation. Please write a 500-word Bible study on the topic of "{desired_topic}" for "{audience}". The passage you will be focusing on is:

---
{passage}---

Please ensure that the study connects deeply with the congregation's real-life challenges. A well-crafted Bible study should go beyond doctrinal teachings to explore the text's original intent and practical application for believers today. This involves thoroughly understanding the text's purpose as inspired by the Holy Spirit and its relevance to contemporary life.

Additionally, ensure that the Bible study engages with the Fallen Condition Focus (FCF), verifying that it addresses human fallenness with divine solutions as outlined in Scripture. The Bible study should identify the FCF, maintain a God-centered perspective, and guide believers toward a biblical response, emphasizing divine grace and the text's relevance to spiritual growth. This dual focus on purposeful interpretation and practical application underpins a compelling Bible study.

An effective Bible study requires the Fallen Condition Focus (FCF) to be addressed, as this is central to discerning whether the message fulfills its purpose of speaking to the human condition in light of Scripture. To do so, one must examine if the Bible study clearly articulates the specific problem or need (not necessarily a sin) that the passage aims to address, demonstrating how Scripture speaks directly to real-life concerns. The FCF should be specific and relevant, enabling {audience} to see the immediate significance of the message in their lives. A well-evaluated Bible study will present the text accurately and connect deeply with the listeners by addressing their shared human experiences and conditions, as highlighted in the original context of the Scripture and its application today.

Moreover, the effectiveness of a Bible study is also measured by its application—the "so what?" factor that moves beyond mere exposition to practical, life-changing instruction. Ensure that the Bible study transitions smoothly from doctrinal truths to actionable applications, offering clear, Scripture-based guidance for living out the teachings of the Bible in everyday situations. This includes checking if the sermon provides a Christ-centered solution to the FCF, steering clear of simplistic, human-centered fixes, and encouraging listeners toward transformation in the likeness of Christ. A sermon that effectively articulates and applies the FCF, thereby meeting the spiritual needs of the audience with biblical fidelity and practical relevance, is considered well-crafted and impactful.

I greatly value your thorough analysis. Please provide a detailed Bible study that meets these criteria on the topic of "{desired_topic}" for "{audience}" drawn from {reference}. Write it as engagingly as possible, ensuring that it is both theologically sound and practically relevant to the lives of {audience}, avoiding unnecessary jargon. Listeners usually don't understand when you use the term "Fallen Condition Focus (FCF)", please avoid it. Instead, focus on the real-life challenges and practical applications of the passage. Ensure that the Bible study is engaging, theologically sound, and practically relevant to the lives of {audience}. Your Bible study should be 500-word long, providing a clear, concise, and compelling message, remembering that not all the your listeners are familiar with the Bible or are even Christians. Please share the Gospel in a way that is clear and accessible to all."""
    
    return message

def generate_draft(passage, reference, desired_topic, audience):

    message = generate_first_message(passage, reference, desired_topic, audience)

    response = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": STUDY_GEN_SYS_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature = 0
    )
    return response.choices[0].message.content

calvin_sys_message = f"""{CALVIN_SYS_PROMPT} You are here to ensure that the Bible study is theologically sound and faithful to the Scriptures."""

def generate_review_message(draft, reference, desired_topic, audience):
    message = f"""You are reviewing a Bible study written by a Pastor of the Silicon Valley Reformed Baptist Church. The study is on the topic of "{desired_topic}" for "{audience}". The passage focused on is {reference}. Please provide a detailed review of the Bible study, ensuring that it is theologically sound and faithful to the Scriptures. Your review should offer constructive feedback on the study's interpretation, application, and overall effectiveness in communicating the message of the Bible for {audience}. Here is the Bible study for your review:

---
{draft}
---

Your insights will help the Pastor refine the study and ensure that it aligns with the teachings of the Bible and the 1689 London Baptist Confession of Faith. I greatly value your thorough analysis. Please provide a detailed review of the Bible study, highlighting its strengths and areas for improvement. Your review should be insightful, constructive, and focused on enhancing the study's theological accuracy and practical relevance for {audience}."""
    
    return message

def generate_review(draft, reference, desired_topic, audience):

    message = generate_review_message(draft, reference, desired_topic, audience)

    response = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": calvin_sys_message},
            {"role": "user", "content": message}
        ],
        temperature = 0
    )
    return response.choices[0].message.content


def generate_final_study(passage, reference, desired_topic, audience, draft, review):

    og_message = generate_first_message(passage, reference, desired_topic, audience)

    new_message = f"Thank you for creating the draft. {review}.\n\nPlease use this feedback to revise your Bible study. Remember to share the gospel, in case there are listeners that aren't Christians. I greatly value your thorough analysis."

    response = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": STUDY_GEN_SYS_PROMPT},
            {"role": "user", "content": og_message},
            {"role": "system", "content": draft},
            {"role": "user", "content": new_message}
        ],
        temperature = 0
    )
    return response.choices[0].message.content