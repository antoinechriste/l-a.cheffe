# Import libraries
from langchain_community.document_loaders import PyPDFium2Loader
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from pathlib import Path
from langchain.chains import RetrievalQA

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
text_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.LATEX, chunk_size=60, chunk_overlap=0
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
retriever = vectordb.as_retriever(search_kwargs={"k": 2})
query = "Efficient parameter tuning"
query = "Key Advantages of LoRA"
docs = retriever.invoke(query)
docs

# Task 6: Construct a QA Bot that leverages the LangChain and Mistral LLM

def get_llm():
    """Initialize and return the Mistral LLM using HuggingFace Hub."""
    return HuggingFaceHub(
        repo_id="mistralai/mistral-small-3-1-24b-instruct-2503",
        model_kwargs={
            "temperature": 0.1,  # More focused responses
            "max_length": 512,   # Reasonable response length
            "top_p": 0.95       # Maintain output quality
        }
    )

def retriever(vectorstore):
    """Create a retriever from the vector store."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}  # Return top 3 most relevant chunks
    )

def retriever_qa(vectorstore, query):
    """
    """
    llm = get_llm()
    retriever_obj = retriever(vectorstore)
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Simple chain that "stuffs" all retrieved docs into prompt
        retriever=retriever_obj,
        return_source_documents=True  # Include source docs in response
    )
    
    response = qa.invoke({"query": query})
    return response['result']

# Example usage
if __name__ == "__main__":
    # Example questions to test the QA system
    test_questions = [
        "What is the main topic of this paper?",
    ]

    print("\nTesting QA System:")
    for question in test_questions:
        print(f"\nQ: {question}")
        try:
            answer = retriever_qa(vectordb, question)
            print(f"A: {answer}")
        except Exception as e:
            print(f"Error: {str(e)}")
