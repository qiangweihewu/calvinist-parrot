from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from tqdm import tqdm
import time, openai, os, re, shutil

# load environment variables
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# if temp forlder doesn't exist, create it
if not os.path.exists('temp'):
    os.makedirs('temp')

def extract_title_and_creators(filename):
    filename = os.path.join(os.getcwd(), filename)
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expressions to match title and creator(s)
    title_pattern = re.compile(r'Title:\s*(.+?)(?=Creator)', re.MULTILINE | re.DOTALL)
    creator_pattern = re.compile(r'Creator\(s\):\s*(.+?)(?=Print Basis:)', re.MULTILINE | re.DOTALL)

    # Regular expression to find instances of "Image of page 1" or "Image of page 2" etc.
    image_pattern = re.compile(r'Image of page \d+')

    # If content has more than 3 instances of "Image of page 1" or "Image of page 2" etc., then it is not a book
    if len(image_pattern.findall(content)) > 3:
        return '', '', False
    else:
        # Extract title and creators from the content
        title_match = title_pattern.search(content)
        title = title_match.group(1).strip() if title_match else ''
        title = [title.strip() for title in title.split('\n') if title.strip()]
        title = ' '.join(title)

        creator_match = creator_pattern.search(content)
        creators = creator_match.group(1).strip() if creator_match else ''
        creators = [creator.strip() for creator in creators.split('\n') if creator.strip()]
        creators = ' - '.join(creators)

        return title, creators, True

def get_formatted_sources_ccel(response):
    """Get formatted sources text."""
    texts = []
    books = []
    for source_node in response.source_nodes:
        if source_node.node.metadata['title'] not in books:
            books.append(source_node.node.metadata['title'])
            source_text = f"\nTitle: {source_node.node.metadata['title']}\nCreators: {source_node.node.metadata['creators']}\nScore: {source_node.score:.4f}"
            texts.append(source_text)
    return "\n\n".join(texts)

list_of_files = os.listdir('ccel')
print(f'\nWe have {len(list_of_files)} files in the library')

service_context = ServiceContext.from_defaults(chunk_size_limit=1024)

start = time.time()
ccel_index = VectorStoreIndex([], service_context=service_context)
no_text = []
kg_docs = []

print('\nLoading documents...')

for file in tqdm(list_of_files):
    shutil.copy(f'ccel/{file}', 'temp/temp.txt')
    documents = SimpleDirectoryReader('temp').load_data()
    title, creators, validation = extract_title_and_creators(f'ccel\\{file}')
    if validation:
        for doc in documents:
            doc.metadata['title'] = title
            doc.metadata['creators'] = creators
            ccel_index.insert(doc)
            kg_docs.append(doc)
    else:
        no_text.append(file)

print(f'\nIndex populated in {(time.time() - start)/60:.3f} minutes')

total_cost = (ccel_index._service_context.embed_model._total_tokens_used/1000) * 0.0001 
print('\nTotal cost: $', total_cost)
print('\nNumber of files with no text: ', len(no_text))


ccel_index.storage_context.persist(persist_dir='ccel_index')