from dotenv import load_dotenv
from serpapi import GoogleSearch
import pythonbible as bible
from bs4 import BeautifulSoup
from datetime import datetime as dt
import pytz
import os, requests
from parrot_toolkit.sql_models import Devotionals
from parrot_ai.core.prompts import DEVOTIONAL_SYS_PROMPT

import pandas as pd

bsb = pd.read_csv('app/bsb.tsv', sep='\t')

load_dotenv()

gpt_model = os.environ.get("GPT_MODEL")

from openai import OpenAI
client = OpenAI()

et = pytz.timezone('US/Eastern')

from sqlalchemy.orm import sessionmaker
import google_connector as gc

# create engine
pool = gc.connect_with_connector('parrot_db')

# if temp folder doesn't exist create it
if not os.path.exists('temp'):
    os.makedirs('temp')

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

def get_article(soup, found=False):
    # Find all the <div> elements on the page
    divs = soup.find_all('div')
    start = len(divs)

    # Calculate the length of the text in each <div> element
    div_text_lengths = [len(div.text) for div in divs]

    # Find the index of the <div> element with the longest text
    max_index = div_text_lengths.index(max(div_text_lengths))

    # Select the <div> element with the longest text
    longest_div = divs[max_index]
    end = len(longest_div.find_all('div'))
    
    if end == 0:
        article = soup.text
        article = article.replace('\n', '').replace('\xa0', ' ').replace('\t', ' ').replace('\r', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
        return " ".join(article.split(' ')[:50])
    
    found = False if start - end < 50 else True

    if found:
        article = longest_div.text
        article = article.replace('\n', '').replace('\xa0', ' ').replace('\t', ' ').replace('\r', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
        return " ".join(article.split(' ')[:50])
    else:
        return get_article(longest_div, False)
    
def fech_news():
    articles = []
    params = {
        "engine": "google",
        "q": "latest news",
        "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    links = []

    for i in results['top_stories'][:5]:
        links.append(i['link'])
        response = requests.get(i['link'])
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div')
        if len(divs) != 0:
            articles.append(f"{i['title']} - {get_article(soup)}")

    return articles, "\n - ".join(links)




def generate_message(devotional_type, now, latest_news):
    message = f"""You are writing a {devotional_type} devotional for {now.strftime('%A, %B %d, %Y')}.

Here are snippets of the latest news:

---------------------

{latest_news}

---------------------

Please output a response as JSON with the following format:

{{
    "bible_verse": string, \\ The Bible verse reference of the passage you are using (e.g. Romans 3.10-12)
    "title": string \\ The title of your devotional
    "devotional": string \\ The devotional text, in the style of Charles Spurgeon's Morning and Evening Devotionals
}}

If it's a morning devotional, focus on encouraging people on growing on their faith, if it's an evening devotional, focus on conforting people on their faith. Remember that you are writing for other reformed believers. They can either believe on the 1689 London Baptist Confession of Faith or the Westminster Confession of Faith. Write it in the style of Charles Spurgeon's Morning and Evening Devotionals. Always return response as JSON."""
    
    return message

def generate_devotional():
    now = dt.now(et)
    devotional_type = "evening" if now.hour >= 17 or now.hour < 5 else "morning"
    print('Getting news...')
    articles, links = fech_news()
    latest_news = "\n\n---\n\n".join(articles)
    id = now.strftime("%Y_%m_%d")
    id += f"_{devotional_type}_devotional"

    message = generate_message(devotional_type, now, latest_news)

    response = client.chat.completions.create(
        model=gpt_model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": DEVOTIONAL_SYS_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature = 0
    )
    devotional_data = response.choices[0].message.content
    try:
        devotional_data = eval(devotional_data)
        success = True
    except:
        success = False
    
    if success:
        Session = sessionmaker(bind=pool)
        devotionals = Devotionals(
            devotionals_id=id,
            news_articles=links,
            bible_verse=devotional_data['bible_verse'],
            title=devotional_data['title'],
            devotional_text=devotional_data['devotional']
        )
        session = Session()
        session.add(devotionals)
        session.commit()
        session.close()
    else:
        print(devotional_data)
        print('Error generating devotional')
        generate_devotional()

# function to check if devotional exists based on devotional id
def check_if_devotional_exists(devotional_id):
    # create session
    Session = sessionmaker(bind=pool)
    session = Session()

    # query the database
    devotional = session.query(Devotionals).filter_by(devotionals_id=devotional_id).first()

    # close the session
    session.close()

    return devotional

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

    return text_out