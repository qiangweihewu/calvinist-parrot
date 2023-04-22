from llama_index import SimpleDirectoryReader, GPTSimpleVectorIndex
from llama_index.node_parser import SimpleNodeParser

from dotenv import load_dotenv
load_dotenv()

documents = SimpleDirectoryReader('library').load_data()

parser = SimpleNodeParser()

nodes = parser.get_nodes_from_documents(documents)

index = GPTSimpleVectorIndex(nodes)

index.save_to_disk('christian_index.json')