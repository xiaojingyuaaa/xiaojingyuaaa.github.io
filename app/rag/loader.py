import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    UnstructuredFileLoader,
    UnstructuredMarkdownLoader,
    UnstructuredExcelLoader,
)
from langchain.docstore.document import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mapping from file extension to specific loader
LOADER_MAPPING = {
    ".md": (UnstructuredMarkdownLoader, {}),
    ".txt": (UnstructuredFileLoader, {}),
    ".pdf": (UnstructuredFileLoader, {}),
    ".xlsx": (UnstructuredExcelLoader, {}),
    ".xls": (UnstructuredExcelLoader, {}),
    ".docx": (UnstructuredFileLoader, {}),
    ".doc": (UnstructuredFileLoader, {}),
}

def load_documents(docs_path: str) -> List[Document]:
    """
    Loads all documents from the specified directory, using different loaders
    for different file types.

    Args:
        docs_path (str): The path to the directory containing the documents.

    Returns:
        List[Document]: A list of loaded Document objects.
    """
    path = Path(docs_path)
    if not path.is_dir():
        logging.error(f"The path {docs_path} is not a valid directory.")
        return []

    loaded_documents = []
    for file_path in path.rglob("*.*"):
        ext = file_path.suffix.lower()
        if ext in LOADER_MAPPING:
            loader_class, loader_args = LOADER_MAPPING[ext]
            try:
                logging.info(f"Loading file: {file_path}")
                loader = loader_class(str(file_path), **loader_args)
                loaded_documents.extend(loader.load())
            except Exception as e:
                logging.error(f"Failed to load file {file_path}: {e}", exc_info=True)
        else:
            logging.warning(f"Unsupported file type: {file_path}. Skipping.")

    logging.info(f"Successfully loaded {len(loaded_documents)} documents.")
    return loaded_documents
