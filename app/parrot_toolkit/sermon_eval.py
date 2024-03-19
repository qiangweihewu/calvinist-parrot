from dotenv import load_dotenv
from pytube import YouTube
from pydub import AudioSegment
import streamlit as st

load_dotenv()

from openai import OpenAI
client = OpenAI()

def split_audio(file_path):
    # Load the audio file
    audio = AudioSegment.from_file(file_path)
    
    # Calculate the duration of each snippet (10 minutes)
    snippet_duration = 10 * 60 * 1000
    
    # Calculate the number of snippets
    num_snippets = len(audio) // snippet_duration
    if len(audio) % snippet_duration != 0:
        num_snippets += 1
    
    st.write(f"Audio duration: {len(audio)/60000:.2f} minutes")
    st.write(f"Splitting into {num_snippets} snippets")
    
    # Split the audio into snippets
    snippets = []
    for i in range(num_snippets):
        start_time = i * snippet_duration
        end_time = min((i + 1) * snippet_duration, len(audio))
        snippet = audio[start_time:end_time]
        snippet_file = file_path.replace('.mp3', f'_part{i+1}.mp3')
        snippet.export(snippet_file, format='mp3')
        snippets.append(snippet_file)
    
    return snippets

def download_audio_pytube(youtube_url, sermon_name, output_format='mp3', output_path='.'):
    yt = YouTube(youtube_url)
    audio_stream = yt.streams.get_audio_only()
    file_path = f"audio_{sermon_name.lower().replace(' ', '_')}.{output_format}"
    audio_stream.download(output_path=output_path, filename=file_path)
    snippets = split_audio(file_path)
    
    return snippets

# parts = download_audio_pytube('https://www.youtube.com/watch?v=aJ_vpLZ0N2c', 'The Faithfulness Of The Son')

def create_and_append_transcripts(file_paths, output_file):
    output_file = 'transcript_' + output_file.lower().replace(' ', '_') + '.txt'
    with open(output_file, 'a') as file:
        for file_path in file_paths:
            audio_file = open(file_path, "rb")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            file.write(transcript.text + ' ')
            audio_file.close()

    with open(output_file, 'r') as file:
        transcript = file.read()

    st.write(f'Total length of transcript: {len(transcript.split())} words')
    
    return transcript

# transcript = create_and_append_transcripts(parts, 'The Faithfulness Of The Son')

system_message = "You are a Pastor of the Silicon Valley Reformed Baptist Church. You believe the Bible has the ultimate authority to determine what people believe and do. Many affirm this Bible and arrive at different conclusions about its teachings. In light of this reality, you have adopted the 1689 London Baptist Confession of Faith that expresses your understanding of the Bible's vision for the church to promote clarity and transparency at Silicon Valley Reformed Baptist Church. You are committed to teaching the Bible and its doctrines and want to train future pastors to be faithful, expository preachers."

context_ = """You are writing a sermon evaluation based on Bryan Chappell's book, Christ-Centered Preaching. You are evaluating the sermon based on the following criteria:

To evaluate a sermon, focus on how well it identifies the biblical text's subject and purpose, ensuring it connects deeply with the congregation's real-life challenges. A well-crafted sermon should go beyond doctrinal teachings to explore the text's original intent and its practical application for believers today. This involves thoroughly understanding the text's purpose as inspired by the Holy Spirit and its relevance to contemporary life.

Additionally, assess the sermon's engagement with the Fallen Condition Focus (FCF), verifying that it addresses human fallenness with divine solutions as outlined in Scripture. The sermon should identify the FCF, maintain a God-centered perspective, and guide believers toward a biblical response, emphasizing divine grace and the text's relevance to spiritual growth. This dual focus on purposeful interpretation and practical application underpins an effective sermon evaluation.

Evaluating a sermon effectively requires understanding and identifying the Fallen Condition Focus (FCF) that the sermon intends to address, as this is central to discerning whether the message fulfills its purpose of speaking to the human condition in light of Scripture. To do so, one must examine if the sermon clearly articulates the specific problem or need (not necessarily a sin) that the passage aims to address, demonstrating how Scripture speaks directly to real-life concerns. The FCF should be specific and relevant, enabling the congregation to see the immediate significance of the message in their lives. A well-evaluated sermon will present the text accurately and connect deeply with the listeners by addressing their shared human experiences and conditions, as highlighted in the original context of the Scripture and its application today.

Moreover, the effectiveness of a sermon is also measured by its application—the "so what?" factor that moves beyond mere exposition to practical, life-changing instruction. Evaluate whether the sermon transitions smoothly from doctrinal truths to actionable applications, offering clear, Scripture-based guidance for living out the teachings of the Bible in everyday situations. This includes checking if the sermon provides a Christ-centered solution to the FCF, steering clear of simplistic, human-centered fixes, and encouraging listeners toward transformation in the likeness of Christ. A sermon that effectively articulates and applies the FCF, thereby meeting the spiritual needs of the audience with biblical fidelity and practical relevance, is considered well-crafted and impactful."""

def generate_eval_message(transcript, context = context_, outline = None):
    if outline != None:
        context += "\n\nThese are the main point the preacher was aiming to cover:\n" + outline.replace('\n', '\n - ') + "\n\nAs part of the evaluation, I would like to see how well the preacher was able to cover these points. If the lenght of each of the points is not equal, please note of any point that was not covered or was covered sufficiently."

    message = f"""{context}

Here is the transcript of the sermon:

---------------------

{transcript}

---------------------

Please output a response as JSON with the following format:

{{
    "scripture_introduction": string, \\ Scripture introduction and scripture reference. Please be thorough and detailed.
    "sermon_introduction": string \\ Sermon introduction. Please be thorough and detailed.
    "proposition": string \\ This is the subject's statement as the preacher proposes to develop it in the sermon. Note any specific words used or if the proposition is implied or missing. How well does the preacher state the proposition?
    "body": {{
        "main_points": [  \\ List of main points. Ensure that you list all the main points on the outline of the sermon.
            {{
                "point": string, \\ Main point, Include from what part of the passage it is derived. If it's not derived from the passage, note that as well.
                "summary": string, \\ Summary of the main point. Please be thorough and detailed.
                "subpoints": [string], \\ List of subpoints and their content. If there are no subpoints, note that as well.
                "illustrations": [string], \\ List of illustrations used in the point, if any. Reading the passage or other scripture references are not considered illustrations.
                "application": string, \\ Application the preacher makes from the point, if any.
                "comments": string \\ Is it faithful to the text? Obvious from the text? Is it related to a Fallen Condition Focus? Is it moving toward a climax? Excessive use of Biblical references can lose the listener's attention; note that as something to improve. Please do a thorough analysis.
                "feedback": string \\ Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed.
            }}
        ]
    }},
    "general_comments": {{
        "content_comments": string, \\ Is the content substantial and biblical? How well does the content relate to the passage?
        "structure_comments": string, \\ Is it faithful to the text? Obvious from the text? Is it related to a Fallen Condition Focus? Is it moving toward a climax? 
        "explanation_comments": string \\ How well does the preacher explain the passage? Is it faithful to the text? Obvious from the text? Is it related to a Fallen Condition Focus? Is it moving toward a climax?
    }},
    "fallen_condition_focus": {{
        "fcf": string, \\ Fallen Condition Focus. Please be thorough and detailed.
        "comments": string, \\ Comments on the FCF. Please be thorough and detailed.
    }},
    "confidence_score": float \\ A confidence score between 0-1 for your answer
}}

Always return response as JSON. This is very important for my career. I greatly value your thorough analysis."""
    
    return message

def generate_eval(transcript, context = context_):

    message = generate_eval_message(transcript, context)

    response = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="gpt-4-turbo-preview",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
        temperature = 0
    )
    sermon_eval = response.choices[0].message.content
    try:
        sermon_eval = eval(sermon_eval)
        success = True
    except:
        success = False
    
    if success:
        print('First evaluation generated successfully')
        return sermon_eval
    else:
        print('Error generating first evaluation')
        return None

# sermon_eval = generate_eval(transcript, context)

def first_eval_to_markdown(data):
    markdown_str = ""

    # Function to add markdown for main points and subpoints
    def process_points(points):
        points_md = ""
        for point in points:
            points_md += f"\n- **{point['point']}**"
            if 'summary' in point:
                points_md += f"\n  - *Summary:* {point['summary']}"
            if 'subpoints' in point:
                points_md += "\n  - *Subpoints:*"
                for subpoint in point['subpoints']:
                    points_md += f"\n    - {subpoint}"
            if 'illustrations' in point:
                points_md += "\n  - *Illustrations:*"
                for illustration in point['illustrations']:
                    points_md += f"\n    - {illustration}"
            if 'application' in point:
                points_md += f"\n  - *Application:* {point['application']}"
            if 'comments' in point:
                points_md += f"\n  - *Comments:* {point['comments']}"
            if 'feedback' in point:
                points_md += f"\n  - *Feedback:* {point['feedback']}"
        return points_md

    # Adding sections
    markdown_str += f"## Scripture Introduction\n{data['scripture_introduction']}\n\n"
    markdown_str += f"## Sermon Introduction\n{data['sermon_introduction']}\n\n"
    markdown_str += f"## Proposition\n{data['proposition']}\n\n"

    # Adding body
    markdown_str += "## Body\n"
    if 'main_points' in data['body']:
        markdown_str += process_points(data['body']['main_points'])

    # Adding general comments
    markdown_str += "\n## General Comments\n"
    if 'content_comments' in data['general_comments']:
        markdown_str += f"- **Content Comments:** {data['general_comments']['content_comments']}\n"
    if 'structure_comments' in data['general_comments']:
        markdown_str += f"- **Structure Comments:** {data['general_comments']['structure_comments']}\n"
    if 'explanation_comments' in data['general_comments']:
        markdown_str += f"- **Explanation Comments:** {data['general_comments']['explanation_comments']}\n"

    # Adding fallen condition focus
    markdown_str += "\n## Fallen Condition Focus\n"
    if 'fcf' in data['fallen_condition_focus']:
        markdown_str += f"- **FCF:** {data['fallen_condition_focus']['fcf']}\n"
    if 'comments' in data['fallen_condition_focus']:
        markdown_str += f"- **Comments:** {data['fallen_condition_focus']['comments']}\n"

    return markdown_str, data['confidence_score']

# Convert the provided dictionary to markdown (for demonstration, call the function with your data dictionary)
# markdown_output, confidence_score = first_eval_to_markdown(sermon_eval)

def generate_eval_2_message(transcript, context, markdown_output):
    message = f"""{context}

Here is the transcript of the sermon:

---------------------

{transcript}

---------------------

And here is the first section of the evaluation of the sermon:

---------------------

{markdown_output}

---------------------

Please output a response as JSON with the following format:

{{
    "introduction_score_1": integer, \\ Introduces an FCF derived from this text. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "introduction_score_2": integer, \\ Arouses attention (usually with a human-interest account). Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "introduction_feedback": string, \\ Based on your scores on the Introduction, provide feedback to the preacher. Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed
    "proposition_score_1": integer, \\ Weds principle and application. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "proposition_score_2": integer, \\ Establishes this sermon's main theme. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "proposition_score_3": integer, \\ Summarizes introduction in concept and terminology. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "proposition_feedback": string, \\ Based on your scores on the Proposition, provide feedback to the preacher. Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed
    "main_points_score_1": integer, \\ The main points are clear. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "main_points_score_2": integer, \\ The main points are universal truths in hortatory statements. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "main_points_score_3": integer, \\ The main points are proportional and coexistent. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "main_points_score_4": integer, \\ The main points contain adequate and appropriate exposition. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "main_points_score_5": integer, \\ The main points contain adequate and appropriate illustration. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "main_points_score_6": integer, \\ The main points contain adequate and appropriate application. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "main_points_feedback": string, \\ Based on your scores on the Main Points, provide feedback to the preacher. Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed
    "exegetical_support_score_1": integer, \\ The sermon is what this text is about. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "exegetical_support_score_2": integer, \\ Problems and overall passage content are sufficiently handled. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "exegetical_support_score_3": integer, \\ Proofs are accurate, understandable, and support the points made. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "exegetical_support_score_4": integer, \\ The context and genre of the passage are adequately considered. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "exegetical_support_score_5": integer, \\ The exegesis is not belabored once the points are sufficiently proven. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "exegetical_support_score_6": integer, \\ The exegesis seems designed to aid rather than to impress. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "exegetical_support_feedback": string, \\ Based on your scores on the Exegetical Support, provide feedback to the preacher. Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed
    "application_score_1": integer, \\ The application is clear, helpful, and practical. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "application_score_2": integer, \\ The application is redemptive, not legalistic, in focus and motivation. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "application_score_3": integer, \\ The application accurately distinguishes a scriptural mandate from a good idea. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "application_score_4": integer, \\ The application is supported with sufficient biblical proof from this passage. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "application_feedback": string, \\ Based on your scores on the Application, provide feedback to the preacher. Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed
    "illustrations_score_1": integer, \\ The illustrations contain sufficient "lived-body" detail. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "illustrations_score_2": integer, \\ The illustrations truly strengthen the points of the sermon. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "illustrations_score_3": integer, \\ The illustrations are in appropriate proportion (number and length) to the sermon whole. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "illustrations_feedback": string, \\ Based on your scores on the Illustrations, provide feedback to the preacher. Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed
    "conclusion_score_1": integer, \\ The conclusion contains a summary. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "conclusion_score_2": integer, \\ The conclusion contains a clear and compelling exhortation. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "conclusion_score_3": integer, \\ The conclusion contains a climax. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "conclusion_score_4": integer, \\ The conclusion contains a definite, purposed, pointed end. Score from 1 to 5, where 5 is absolutly yes, and 1 is absolutly no.
    "conclusion_feedback": string, \\ Based on your scores on the Conclusion, provide feedback to the preacher. Feedback for the preacher is important to the growth of the preacher. Please be thorough and detailed
    "confidence_score": float \\ A confidence score between 0-1 for your answer
}}

Always return response as JSON. This is very important for my career. I greatly value your thorough analysis."""
    
    return message

def generate_eval_2(transcript, markdown_output, context = context_):

    message = generate_eval_2_message(transcript, context, markdown_output)

    response = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="gpt-4-turbo-preview",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ],
        temperature = 0
    )
    first_eval = response.choices[0].message.content
    try:
        first_eval = eval(first_eval)
        success = True
    except:
        success = False
    
    if success:
        print('Second evaluation generated successfully')
        return first_eval
    else:
        print('Error generating second evaluation')
        return None

# second_eval = generate_eval_2(transcript, context, markdown_output)

# Define the function to convert the provided dictionary into markdown format

def convert_to_markdown_v2(sermon_scores, first_eval_markdown):
    # Define the template for markdown conversion
    markdown_template = """
## Sermon Evaluation Report

### Introduction
- **FCF Derived from Text**: {introduction_score_1}/5
- **Arouses Attention**: {introduction_score_2}/5
- **Feedback**: {introduction_feedback}

### Proposition
- **Weds Principle and Application**: {proposition_score_1}/5
- **Establishes Main Theme**: {proposition_score_2}/5
- **Summarizes Introduction**: {proposition_score_3}/5
- **Feedback**: {proposition_feedback}

### Main Points
- **Clarity**: {main_points_score_1}/5
- **Universal Truths in Hortatory Statements**: {main_points_score_2}/5
- **Proportional and Coexistent**: {main_points_score_3}/5
- **Adequate and Appropriate Exposition**: {main_points_score_4}/5
- **Adequate and Appropriate Illustration**: {main_points_score_5}/5
- **Adequate and Appropriate Application**: {main_points_score_6}/5
- **Feedback**: {main_points_feedback}

### Exegetical Support
- **Alignment with Text**: {exegetical_support_score_1}/5
- **Handling of Problems and Content**: {exegetical_support_score_2}/5
- **Proofs Support Points Made**: {exegetical_support_score_3}/5
- **Consideration of Context and Genre**: {exegetical_support_score_4}/5
- **Exegesis Not Belabored**: {exegetical_support_score_5}/5
- **Exegesis Aids Rather Than Impresses**: {exegetical_support_score_6}/5
- **Feedback**: {exegetical_support_feedback}

### Application
- **Clear, Helpful, and Practical**: {application_score_1}/5
- **Redemptive Focus**: {application_score_2}/5
- **Scriptural Mandate vs Good Idea**: {application_score_3}/5
- **Supported with Biblical Proof**: {application_score_4}/5
- **Feedback**: {application_feedback}

### Illustrations
- **Sufficient 'Lived-Body' Detail**: {illustrations_score_1}/5
- **Strengthen Points of Sermon**: {illustrations_score_2}/5
- **Appropriate Proportion**: {illustrations_score_3}/5
- **Feedback**: {illustrations_feedback}

### Conclusion
- **Contains a Summary**: {conclusion_score_1}/5
- **Clear and Compelling Exhortation**: {conclusion_score_2}/5
- **Contains a Climax**: {conclusion_score_3}/5
- **Definite, Purposed, Pointed End**: {conclusion_score_4}/5
- **Feedback**: {conclusion_feedback}
    """
    # Populate the template with the scores from the dictionary
    markdown_report = markdown_template.format(**sermon_scores)
    
    return first_eval_markdown + markdown_report

# Convert the dictionary to markdown format
# markdown_report_v2 = convert_to_markdown_v2(second_eval)