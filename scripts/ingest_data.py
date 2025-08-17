import sys
import os
import logging

# Add the project root directory to the Python path
# This allows us to import modules from the 'app' directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.rag.loader import load_documents
from app.rag.vector_store import create_vector_store
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to run the data ingestion process.
    - Loads documents from the source directory.
    - Creates a vector store from the documents.
    """
    logging.info("Starting data ingestion process...")

    # Step 1: Load documents from the specified path in config
    logging.info(f"Loading documents from: {settings.DOCS_PATH}")
    try:
        documents = load_documents(settings.DOCS_PATH)
        if not documents:
            logging.warning("No documents were loaded. Please check the DOCS_PATH and its contents.")
            return
        logging.info(f"Successfully loaded {len(documents)} documents.")
    except Exception as e:
        logging.error(f"An error occurred during document loading: {e}", exc_info=True)
        return

    # Step 2: Create and save the vector store
    try:
        create_vector_store(documents)
    except Exception as e:
        logging.error(f"An error occurred during vector store creation: {e}", exc_info=True)
        return

    logging.info("Data ingestion process completed successfully.")

if __name__ == "__main__":
    # To run this script, execute `python scripts/ingest_data.py` from the project root.
    main()
