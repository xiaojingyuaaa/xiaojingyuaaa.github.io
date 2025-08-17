import logging
from typing import List
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_vector_store(documents: List[Document]):
    """
    Creates a FAISS vector store from a list of documents, saves it to disk.

    Args:
        documents (List[Document]): The documents to be processed.
    """
    if not documents:
        logging.warning("No documents provided to create vector store. Aborting.")
        return

    logging.info("Starting to create vector store...")

    # 1. Split documents into chunks
    logging.info(f"Splitting {len(documents)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    logging.info(f"Created {len(chunks)} text chunks.")

    # 2. Load embedding model
    logging.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
    try:
        # Use HuggingFaceEmbeddings to load the model locally
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'} # Or 'cuda' if you have a GPU
        )
    except Exception as e:
        logging.error(f"Failed to load embedding model: {e}", exc_info=True)
        return

    # 3. Create FAISS vector store from chunks
    logging.info("Creating FAISS vector store from text chunks...")
    try:
        vector_store = FAISS.from_documents(chunks, embeddings)
    except Exception as e:
        logging.error(f"Failed to create FAISS vector store: {e}", exc_info=True)
        return

    # 4. Save the vector store to disk
    logging.info(f"Saving vector store to: {settings.VECTOR_STORE_PATH}")
    try:
        vector_store.save_local(settings.VECTOR_STORE_PATH)
        logging.info("Vector store created and saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save vector store: {e}", exc_info=True)
