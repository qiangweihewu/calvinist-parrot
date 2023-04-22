from llama_index import GPTSimpleVectorIndex

from dotenv import load_dotenv
load_dotenv()

personal_index = GPTSimpleVectorIndex.load_from_disk('christian_index.json')
response = personal_index.query('Who wrote the institues of Christian religion?', response_mode="tree_summarize")

print(response.response)