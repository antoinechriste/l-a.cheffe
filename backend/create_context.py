# Import libraries
from langchain_community.document_loaders import PyPDFium2Loader
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import TextIteratorStreamer
from pathlib import Path
import threading
import gradio as gr
import uuid

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
split_text = text_splitter.split_documents(docs)

# Task 3 - Embed documents using local HuggingFace model
# Download the model locally if not already done
#huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir ./models/all-MiniLM-L6-v2

# Initialize the embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="./models/all-MiniLM-L6-v2",  # Fast, lightweight model good for semantic search
    model_kwargs={'device': 'cpu'}   # Use CPU, change to 'cuda' if you have GPU
)

# Task 4 - Create and configure vector databases to store embeddings
# Create a Chroma vector store from the document chunks
vectordb = Chroma.from_documents(
    documents=split_text,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name=f"collection_{uuid.uuid4()}"
)

print(f"Created vector store with {vectordb._collection.count()} documents")

# Install TinyLLaMA model for local inference
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Task 5 - Task 5: Develop a retriever to fetch document segments based on queries (10 points)
def retrieve_context(query, top_k=3):
    results = vectordb.similarity_search(query, k=top_k)
    context = "\n".join([doc.page_content for doc in results])
    return context

def generate_answer_stream(query):
    context = retrieve_context(query)
    prompt = f"Answer the question using the context below:\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt")
    streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)
    generation_kwargs = dict(inputs, max_new_tokens=300, streamer=streamer)
    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    for new_text in streamer:
        yield new_text


# Test it with Gradio interface
iface = gr.Interface(
    fn=generate_answer_stream,
    inputs="text",
    outputs="text",
    title="TinyLlama QA with Streaming",
    live=True  # Enables live updates
)

iface.launch()
