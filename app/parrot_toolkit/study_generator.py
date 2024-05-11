from dotenv import load_dotenv
import os

load_dotenv()

gpt_model = os.environ.get("GPT_MODEL")

from openai import OpenAI
client = OpenAI()

import pandas as pd
import pythonbible as bible

bsb = pd.read_csv('app/bsb.tsv', sep='\t')

def get_bsb_text(verse):
    return bsb.loc[bsb['Verse'] == verse, 'Berean Standard Bible'].values[0]

def get_text(verse):
    references = bible.get_references(verse)
    text_out = ''

    for i in references:
        text_out += '\n'
        verse_id = bible.convert_reference_to_verse_ids(i)
        reference_out = bible.format_scripture_references([i])
        for j in verse_id:
            temp = bible.convert_verse_ids_to_references([j])
            temp_ref = bible.format_scripture_references(temp)
            try:
                text_out += f'{get_bsb_text(temp_ref)}  \n'
                version = 'BSB'
            except:
                text_out += f'{bible.get_verse_text(j)}  \n'
                version = 'ASV'
        text_out = text_out[:-1]
        text_out += f' - {reference_out} ({version})  \n\n'

    return text_out, reference_out

system_message_parrot = "You are a Pastor of the Silicon Valley Reformed Baptist Church. You believe the Bible has the ultimate authority to determine what people believe and do. Many affirm this Bible and arrive at different conclusions about its teachings. In light of this reality, you have adopted the 1689 London Baptist Confession of Faith that expresses your understanding of the Bible's vision for the church to promote clarity and transparency. You are committed to teaching the Bible and its doctrines in an easy an approchable way that can build up the church."

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
            {"role": "system", "content": system_message_parrot},
            {"role": "user", "content": message}
        ],
        temperature = 0
    )
    return response.choices[0].message.content

calvin_sys_message = """You are John Calvin, the author of the Institutes of the Christian Religion, your magnum opus, which is extremely important for the Protestant Reformation. The book has remained crucial for Protestant theology for almost five centuries. You are a French theologian, pastor, and reformer in Geneva during the Protestant Reformation. You are a principal figure in the development of the system of Christian theology later called Calvinism. You are known for your teachings and writings, particularly in the areas of predestination and the sovereignty of God in salvation. You are committed to the authority of the Bible and the sovereignty of God in all areas of life. You are known for your emphasis on the sovereignty of God, the authority of Scripture, and the depravity of man. You are here to ensure that the Bible study is theologically sound and faithful to the Scriptures."""

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

    new_message = f"Thank you creating the draft. {review}.\n\nPlease use this feedback to revise your Bible study. Remember to share the gospel, in case there are listeners that aren't Christians. I greatly value your thorough analysis."

    response = client.chat.completions.create(
        model=gpt_model,
        messages=[
            {"role": "system", "content": system_message_parrot},
            {"role": "user", "content": og_message},
            {"role": "system", "content": draft},
            {"role": "user", "content": new_message}
        ],
        temperature = 0
    )
    return response.choices[0].message.content