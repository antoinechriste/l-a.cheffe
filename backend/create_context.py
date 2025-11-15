# Import libraries
from langchain_community.document_loaders import PyPDFium2Loader
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from pathlib import Path
import gradio as gr

# Task 1 - Load URLs from url_list.txt
path_url = "C:\\Users\\chris\\OneDrive\\Documenti\\AI-projects\\cookbot\\documents\\"

# Read URLs from url_list.txt
url_file = Path(path_url) / "url_list.txt"
urls = []
if url_file.exists():
    with open(url_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(urls)} URLs from url_list.txt")
    if urls:
        loader = WebBaseLoader(urls)
        docs = loader.load()
        print(f"Successfully loaded content from {len(docs)} URLs")
    else:
        print("No URLs found in url_list.txt")
        docs = []
else:
    print(f"URL list file not found: {url_file}")
    docs = []

# Add custom recipes from local pdf
pdf_path = Path(path_url) / "recettes.pdf"
if pdf_path.exists():
    pdf_loader = PyPDFium2Loader(str(pdf_path))
    pdf_docs = pdf_loader.load()
    docs.extend(pdf_docs)  # Append PDF contents to existing docs from URLs
    print(f"Loaded {len(pdf_docs)} pages from recettes.pdf")
else:
    print(f"PDF file not found: {pdf_path}")

# Task 2 - Code splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,       # Taille idéale pour recettes
    chunk_overlap=80,     # Pour éviter de couper une étape
    separators=["\n\n", "\n", ".", ";", " "]  # Ajout du point-virgule pour le français
)

# Split all loaded documents (use page_content when available)
texts_to_split = [d.page_content if getattr(d, 'page_content', None) is not None else str(d) for d in docs]
split_text = text_splitter.create_documents(texts_to_split)


# Task 3 - Embed documents using local HuggingFace model
# Download the model locally if not already done
#huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir ./models/all-MiniLM-L6-v2

# Initialize the embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="./models/all-MiniLM-L6-v2",  # Fast, lightweight model good for semantic search
    model_kwargs={'device': 'cpu'}   # Use CPU, change to 'cuda' if you have GPU
)

texts = [doc.page_content for doc in split_text]
doc_result = embeddings.embed_documents(texts)

# Task 4 - Create and configure vector databases to store embeddings
# Create a Chroma vector store from the document chunks
vectordb = Chroma.from_documents(
    documents=split_text,  # Use split_text (Document objects) instead of texts (strings)
    embedding=embeddings,
    persist_directory="./chroma_db"  # Optionally persist to disk
)

print(f"Created vector store with {vectordb._collection.count()} documents")

# Task 5 - Task 5: Develop a retriever to fetch document segments based on queries (10 points)
query = "Quelle est la meilleure recette de smashed burger?"
results = vectordb.similarity_search(query, k=3)

for i, doc in enumerate(results, start=1):
    print(f"\nResult {i}:")
    print(doc.page_content)
    print("Metadata:", doc.metadata)

# Test it with Gradio interface
def query_chroma(user_query):
    results = vectordb.similarity_search(user_query, k=3)
    return "\n\n".join([doc.page_content for doc in results])

gr.Interface(fn=query_chroma, inputs="text", outputs="text", title="L-A.cheffe").launch()

