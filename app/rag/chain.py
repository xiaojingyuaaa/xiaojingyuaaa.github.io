import logging
from typing import List, Tuple, Dict, Any, Optional

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import format_document
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableMap
from langchain.prompts.prompt import PromptTemplate

from app.core.config import settings
from app.rag.prompts import QA_PROMPT, CONTEXTUALIZE_Q_PROMPT, qa_template_str

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. Load necessary components ---

def get_llm():
    """Initializes and returns the LLM client."""
    logging.info("Initializing LLM client...")
    try:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            openai_api_base=settings.VLLM_API_BASE,
            openai_api_key=settings.VLLM_API_KEY,
            temperature=0.1,  # Lower temperature for more factual answers
            streaming=True
        )
        logging.info("LLM client initialized successfully.")
        return llm
    except Exception as e:
        logging.error(f"Failed to initialize LLM: {e}", exc_info=True)
        raise

def get_embeddings():
    """Initializes and returns the embedding model."""
    logging.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'}  # Change to 'cuda' if GPU is available
        )
        logging.info("Embedding model loaded successfully.")
        return embeddings
    except Exception as e:
        logging.error(f"Failed to load embeddings: {e}", exc_info=True)
        raise

def get_retriever(embeddings):
    """Initializes and returns the FAISS retriever."""
    vector_store_path = settings.VECTOR_STORE_PATH
    logging.info(f"Loading vector store from: {vector_store_path}")
    try:
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4}) # Retrieve top 4 documents
        logging.info("Retriever initialized successfully.")
        return retriever
    except Exception as e:
        logging.error(f"Failed to load vector store or create retriever: {e}", exc_info=True)
        raise

# --- 2. Define chain components ---

def _format_chat_history(chat_history: List[Tuple[str, str]]) -> str:
    """Formats chat history into a readable string."""
    buffer = []
    for human, ai in chat_history:
        buffer.append(f"Human: {human}\nAI: {ai}")
    return "\n".join(buffer)

# Default document prompt is just the page content
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    """Combines documents into a single string."""
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

# --- 3. Construct the RAG chain ---

def create_rag_chain():
    """
    Creates and returns the full RAG chain with history and source tracking.
    """
    try:
        # Initialize all components
        llm = get_llm()
        embeddings = get_embeddings()
        retriever = get_retriever(embeddings)

        # This chain rephrases the user's question based on chat history
        contextualize_q_chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: _format_chat_history(x["chat_history"])
            )
            | CONTEXTUALIZE_Q_PROMPT
            | llm
            | StrOutputParser()
        )

        # This chain forms the main RAG logic
        qa_chain = (
            RunnablePassthrough.assign(
                context=RunnableLambda(
                    lambda x: contextualize_q_chain.invoke(x) if x.get("chat_history") else x["question"]
                )
                | retriever
                | _combine_documents
            )
            | QA_PROMPT
            | llm
        )

        # The final chain that returns the AI message and the source documents
        rag_chain = RunnableMap(
            {
                "answer": qa_chain,
                "source_documents": (
                    RunnableLambda(
                        lambda x: contextualize_q_chain.invoke(x) if x.get("chat_history") else x["question"]
                    )
                    | retriever
                ),
            }
        )
        logging.info("RAG chain created successfully.")
        return rag_chain

    except Exception as e:
        logging.error(f"Error creating RAG chain: {e}", exc_info=True)
        return None

# --- Entry point to get the chain ---
# This is a singleton pattern to avoid re-initializing the chain on every request
rag_chain_instance = None

def get_rag_chain():
    """Returns a singleton instance of the RAG chain."""
    global rag_chain_instance
    if rag_chain_instance is None:
        rag_chain_instance = create_rag_chain()
    return rag_chain_instance
