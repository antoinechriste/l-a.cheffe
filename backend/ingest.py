"""
Ingestion script to convert PDFs (or text files) into vector embeddings and store them in Chroma.

Usage:
  python ingest.py                # ingest all PDFs under ./data/documents
  python ingest.py --file path    # ingest a single file
  python ingest.py --reindex       # re-create the Chroma DB from scratch

This script uses:
 - langchain_community.document_loaders (PyPDFium2Loader / PyMuPDFLoader)
 - langchain_text_splitters.RecursiveCharacterTextSplitter
 - langchain_community.embeddings.HuggingFaceEmbeddings
 - langchain_community.vectorstores.Chroma

It writes the Chroma persistence to ./chroma_db by default.
Make sure required packages are installed in your Python environment.
"""

from pathlib import Path
import argparse
import sys
import os
import json

# Choose loaders and embeddings from langchain-community
from langchain_community.document_loaders import PyPDFium2Loader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data' / 'documents'
CHROMA_DIR = BASE_DIR / 'chroma_db'

# Default embedding model (local SentenceTransformers / HF repo)
DEFAULT_EMBED_MODEL = os.environ.get('EMBED_MODEL', 'all-MiniLM-L6-v2')


def find_loader_for_path(path: Path):
    """Select an appropriate loader class for the file extension."""
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        # prefer PyMuPDFLoader if available
        if PyMuPDFLoader is not None:
            return PyMuPDFLoader
        if PyPDFium2Loader is not None:
            return PyPDFium2Loader
        raise RuntimeError('No PDF loader available. Install pymupdf or pypdfium2.')
    # for simple text files, create a tiny loader wrapper
    if suffix in ('.txt', '.md'):
        class _TextLoader:
            def __init__(self, p):
                self.p = p

            def load(self):
                with open(self.p, 'r', encoding='utf-8', errors='ignore') as f:
                    return [type('Doc', (), {'page_content': f.read()})()]

        return _TextLoader

    raise RuntimeError(f'Unsupported file type: {suffix}')


def load_documents(path: Path):
    loader_cls = find_loader_for_path(path)
    loader = loader_cls(str(path))
    docs = loader.load()
    # ensure we return list of Document-like objects with page_content
    return docs


def split_documents(docs, chunk_size=800, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # docs can be list of str or Document-like; create_documents expects list[str]
    texts = [d.page_content if getattr(d, 'page_content', None) is not None else str(d) for d in docs]
    chunks = splitter.create_documents(texts)
    return chunks


def get_embeddings(model_name=DEFAULT_EMBED_MODEL, device='cpu'):
    print(f'Initializing embeddings model: {model_name} (device={device})')
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': device})


def index_documents(chunks, embeddings, persist_directory=CHROMA_DIR, collection_name='cookbot_documents'):
    # Create/open Chroma and add documents (documents are langchain Document objects)
    print(f'Indexing {len(chunks)} chunks into Chroma at {persist_directory}...')
    vectordb = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=str(persist_directory), collection_name=collection_name)
    # Persist to disk (Chroma client may persist automatically depending on implementation)
    try:
        vectordb.persist()
    except Exception:
        # some implementations persist on creation; tolerate absence
        pass
    print('Indexing complete.')
    return vectordb


def ingest_file(path: Path, embeddings, reindex=False):
    print(f'Ingesting file: {path}')
    docs = load_documents(path)
    if not docs:
        print('No text extracted, skipping.')
        return 0
    chunks = split_documents(docs)
    # Optionally reindex: remove previous DB and recreate
    if reindex and CHROMA_DIR.exists():
        import shutil
        print('Removing existing Chroma DB...')
        shutil.rmtree(CHROMA_DIR)
    index_documents(chunks, embeddings)
    return len(chunks)


def ingest_all(embeddings, reindex=False):
    if not DATA_DIR.exists():
        print(f'No documents folder found at {DATA_DIR}. Create it and add files to ingest.')
        return
    files = sorted(list(DATA_DIR.glob('*.*')))
    total = 0
    for f in files:
        try:
            total += ingest_file(f, embeddings, reindex=reindex)
        except Exception as e:
            print(f'Failed to ingest {f}: {e}')
    print(f'Total chunks indexed: {total}')


def main():
    parser = argparse.ArgumentParser(description='Ingest documents into Chroma vector DB')
    parser.add_argument('--file', '-f', help='Path to a single file to ingest')
    parser.add_argument('--reindex', action='store_true', help='Remove existing Chroma DB and reindex')
    parser.add_argument('--model', default=os.environ.get('EMBED_MODEL', DEFAULT_EMBED_MODEL), help='Embedding model name')
    parser.add_argument('--device', default='cpu', help='Device for embeddings (cpu or cuda)')
    args = parser.parse_args()

    embeddings = get_embeddings(model_name=args.model, device=args.device)

    if args.file:
        p = Path(args.file)
        if not p.exists():
            print('File not found:', p)
            sys.exit(1)
        ingest_file(p, embeddings, reindex=args.reindex)
    else:
        ingest_all(embeddings, reindex=args.reindex)


if __name__ == '__main__':
    main()
