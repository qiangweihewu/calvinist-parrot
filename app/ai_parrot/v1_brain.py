import re, os
import pandas as pd
import pythonbible as bible
from dotenv import load_dotenv
load_dotenv()

bsb = pd.read_csv('app/bsb.tsv', sep='\t')

def get_bsb_text(verse):
    return bsb.loc[bsb['Verse'] == verse, 'Berean Standard Bible'].values[0]

gpt_model = os.environ.get("GPT_MODEL")

from openai import OpenAI
client = OpenAI()

parrot_sys_message = """You are /parrot/. You are a member of the Silicon Valley Reformed Baptist Church. You believe the Bible has the ultimate authority to determine what people believe and do. Many affirm this Bible and arrive at different conclusions about its teachings. In light of this reality, we have adopted the 1689 London Baptist Confession of Faith that expresses our understanding of the Bible's vision for the church to promote clarity and transparency at Silicon Valley Reformed Baptist Church. You are among other Christians that trust in the 1689—no need to hold back your thoughts. 

This chat follows the following format:

role: 'user' // /human/ - the question you must answer.
role: 'assistant' // /parrot/ this is you. Please think step by step to ensure you reply biblically and following the 1689.
role: 'user' // /calvin/ Another AI model like you is trying to help you think more biblically to reflect upon your answer. He is your friend.
role: 'assistant' // /parrot/ you get another turn before /human/ talks again. Review your previous answer and ponder if you missed something based on /calvin/'s feedback.
role: 'user' // /human/ - a follow-up question.

Remember that after Calvin, you get another shot. You are *not* /human/.

You and /calvin/ are here to help /human/ learn about the Bible and teach the user what we believe the Bible teaches. When referring to /calvin/, say, Calvin, without the slash. When referring to /human/, say human, without the slash. /calvin/ is your friend and calls you Parrot, and you call him Calvin.

If instead of /human/ you see a name, like John, or Jegama, you should address the user by their name.
"""

calvin_sys_message = """You are John Calvin, the author of the Institutes of the Christian Religion, your magnum opus, which is extremely important for the Protestant Reformation. The book has remained crucial for Protestant theology for almost five centuries. 

This chat follows the following format:

role: 'user' // /human/ - the question you must answer.
role: 'user' // /parrot/ it's another AI model like you; he is a Silicon Valley Reformed Baptist Church member.
role: 'assistant' // You ask the /parrot/ thoughtful questions to reflect upon his answers to the user to ensure his answers are biblically accurate.
role: 'user' // /parrot/ he gets another turn before /human/ talks again.
role: 'user' // /human/ - a follow-up question.

You and /parrot/ are here to help the user /human/ learn about the Bible and teach him what we believe the Bible teaches. You want to ensure that the /parrot/'s responses are accurate and grounded on what you wrote in your Institutes of the Christian Religion book. 

When referring to /human/, say human, without the slash. When referring to /parrot/ say, Parrot, without the slash. /parrot/ is your friend and calls you Calvin, and you call him Parrot.

If instead of /human/ you see a name, like John, or Jegama, you should address the user by their name."""

def get_response(messages_list, stream=True):
    response = client.chat.completions.create(
        model=gpt_model,
        messages=messages_list,
        stream=stream,
        temperature = 0
    )
    return response

def extractQuestions(text):
    pattern = r"\/\/(.*?)\/\/"
    questions = re.findall(pattern, text)
    return questions

def generate_conversation_name(current_conversation):
    prompt_create_name = f"""I have this conversation:

---------------------
{current_conversation}
---------------------

What would you like to name this conversation? It can be a short name to remember this conversation.

Please reply in the following JSON format:

{{
    "name": string \\ Name of the conversation
}}

Always return response as JSON."""


    get_name_prompt = [
        {"role": "system", "content": 'You are a helpful assistant that can create short names for conversations.'}, {"role": "user", "content": prompt_create_name}
    ]

    response = client.chat.completions.create(
        model=gpt_model,
        response_format={ "type": "json_object" },
        messages=get_name_prompt,
        temperature = 0
    )
    conversation_name = response.choices[0].message.content
    try:
        conversation_name = eval(conversation_name)['name']
        return conversation_name
    except:
        return None

def get_references(verse):
    references = bible.get_references(verse)
    output = []
    references_out_list = []

    for i in references:
        text_out = ''
        verse_id = bible.convert_reference_to_verse_ids(i)
        reference_out = bible.format_scripture_references([i])
        references_out_list.append(reference_out)
        for j in verse_id:
            temp = bible.convert_verse_ids_to_references([j])
            temp_ref = bible.format_scripture_references(temp)
            try:
                text_out += f'{get_bsb_text(temp_ref)}  \n'
                version = 'BSB'
            except:
                try:
                    text_out += f'{bible.get_verse_text(j)}  \n'
                    version = 'ASV'
                except:
                    version = '_N/A_'
        text_out = text_out[:-1]
        text_out += f' - {reference_out} ({version})  \n\n'
        output.append(text_out)

    return output, references_out_list

def parse_footnotes(message):
    output, references_out_list = get_references(message)
    other = []
    if len(references_out_list) == 0:
        return message, other
    else:
        for i, v in enumerate(references_out_list):
            if v in message:
                tooltip_text = output[i].replace('\n', '').replace('  ', ' ').strip()
                message = message.replace(
                    v, 
                    f'<span style="text-decoration: underline; cursor: help;" title="{tooltip_text}">{v}</span>'
                )
            else:
                if '_N/A_' not in output[i]:
                    other.append(output[i])
        return message, other