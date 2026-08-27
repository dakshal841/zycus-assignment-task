import os
import glob
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

chroma_client = chromadb.Client()

# Free, local embedding model
local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="support_kb", 
    embedding_function=local_ef
)


def ingest_knowledge_base(kb_dir: str = "data/"):
    """Reads all markdown files and loads them into the vector store."""
    if collection.count() > 0:
        return # Already ingested
    
    # Recursively find all markdown files
    kb_files = glob.glob(os.path.join(kb_dir, "**/*.md"), recursive=True)
    
    documents = []
    metadatas = []
    ids = []
    
    for i, file_path in enumerate(kb_files):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            filename = os.path.basename(file_path)
            
            documents.append(content)
            metadatas.append({"filename": filename})
            ids.append(f"doc_{i}")
            
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Ingested {len(documents)} KB documents into ChromaDB.")

def retrieve_relevant_kb(query: str, n_results: int = 1) -> str:
    """Searches the KB for the most relevant document based on the ticket text."""
    if collection.count() == 0:
        ingest_knowledge_base()
        
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    if results['documents'] and results['documents'][0]:
        doc_content = results['documents'][0][0]
        doc_filename = results['metadatas'][0][0]['filename']
        return f"Document: {doc_filename}\n\n{doc_content}"
    
    return ""

# Run ingestion immediately upon import
ingest_knowledge_base()