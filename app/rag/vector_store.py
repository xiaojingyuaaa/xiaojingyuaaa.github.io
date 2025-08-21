import logging
from typing import List
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_vector_store(documents: List[Document]):
    """
    从文档列表创建FAISS向量数据库，并将其保存到磁盘。

    这个函数执行了RAG流程中的“Indexing”（索引）部分的关键步骤：
    1.  文本分割 (Splitting)
    2.  向量化 (Embedding)
    3.  存储与索引 (Storing & Indexing)

    Args:
        documents (List[Document]): 从`loader`模块加载的文档对象列表。
    """
    if not documents:
        logging.warning("没有提供用于创建向量数据库的文档。正在中止。")
        return

    logging.info("开始创建向量数据库...")

    # 1. 将文档分割成更小的块 (Chunks)
    logging.info(f"正在将 {len(documents)} 个文档分割成文本块...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,       # 每个块的最大字符数
        chunk_overlap=200,     # 块之间的重叠字符数
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    logging.info(f"已创建 {len(chunks)} 个文本块。")

    # 2. 加载嵌入模型 (Embedding Model)
    logging.info(f"正在加载嵌入模型: {settings.EMBEDDING_MODEL_NAME}")
    try:
        # 使用HuggingFaceEmbeddings类从本地加载SentenceTransformer模型
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'} # 如果有GPU，可以改为 'cuda'
        )
    except Exception as e:
        logging.error(f"加载嵌入模型失败: {e}", exc_info=True)
        return

    # 3. 从文本块创建FAISS向量数据库
    logging.info("正在从文本块创建FAISS向量数据库...")
    try:
        vector_store = FAISS.from_documents(chunks, embeddings)
    except Exception as e:
        logging.error(f"创建FAISS向量数据库失败: {e}", exc_info=True)
        return

    # 4. 将向量数据库保存到本地磁盘
    logging.info(f"正在将向量数据库保存到: {settings.VECTOR_STORE_PATH}")
    try:
        vector_store.save_local(settings.VECTOR_STORE_PATH)
        logging.info("向量数据库已成功创建并保存。")
    except Exception as e:
        logging.error(f"保存向量数据库失败: {e}", exc_info=True)
