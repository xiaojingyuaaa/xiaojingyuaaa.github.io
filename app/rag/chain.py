import logging
from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import format_document
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableMap
from langchain.prompts import PromptTemplate

from app.core.config import settings
from app.rag.prompts import QA_PROMPT, CONTEXTUALIZE_Q_PROMPT

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. 加载必要的组件 ---

def get_llm():
    """初始化并返回大语言模型客户端。"""
    logging.info("正在初始化LLM客户端...")
    try:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            openai_api_base=settings.VLLM_API_BASE,
            openai_api_key=settings.VLLM_API_KEY,
            temperature=0.1,  # 较低的温度使回答更具事实性
            streaming=True    # 开启流式输出
        )
        logging.info("LLM客户端初始化成功。")
        return llm
    except Exception as e:
        logging.error(f"初始化LLM失败: {e}", exc_info=True)
        raise

def get_embeddings():
    """初始化并返回嵌入模型。"""
    logging.info(f"正在加载嵌入模型: {settings.EMBEDDING_MODEL_NAME}")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'}  # 如果有GPU，可改为'cuda'
        )
        logging.info("嵌入模型加载成功。")
        return embeddings
    except Exception as e:
        logging.error(f"加载嵌入模型失败: {e}", exc_info=True)
        raise

def get_retriever(embeddings):
    """初始化并返回FAISS检索器。"""
    vector_store_path = settings.VECTOR_STORE_PATH
    logging.info(f"正在从路径加载向量数据库: {vector_store_path}")
    try:
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})  # 设置检索器返回4个最相关的文档
        logging.info("检索器初始化成功。")
        return retriever
    except Exception as e:
        logging.error(f"加载向量数据库或创建检索器失败: {e}", exc_info=True)
        raise

# --- 2. 定义辅助函数和链组件 ---

def _format_chat_history(chat_history: List[Tuple[str, str]]) -> str:
    """将聊天历史格式化为可读的字符串。"""
    buffer = []
    for role, content in chat_history:
        if role == "user":
            buffer.append(f"用户: {content}")
        else:
            buffer.append(f"助手: {content}")
    return "\n".join(buffer)

# 默认的文档格式化Prompt，仅包含页面内容
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    """将多个文档合并成一个字符串。"""
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

# --- 3. 构建RAG链 ---

def create_rag_chain():
    """
    创建并返回完整的RAG链，该链支持聊天历史和答案溯源。

    这条链是整个系统的“大脑”，它通过LangChain表达式语言（LCEL）将各个组件串联起来。
    """
    try:
        # 初始化所有核心组件
        llm = get_llm()
        embeddings = get_embeddings()
        retriever = get_retriever(embeddings)

        # 这条子链用于根据聊天历史重构用户问题，使其成为一个独立的、无需上下文的问题。
        contextualize_q_chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: _format_chat_history(x["chat_history"])
            )
            | CONTEXTUALIZE_Q_PROMPT
            | llm
            | StrOutputParser()
        )

        # 这是主RAG链的核心逻辑
        qa_chain = (
            RunnablePassthrough.assign(
                # 'context'的生成逻辑：
                # 1. 如果有聊天历史，则先调用contextualize_q_chain生成独立问题，再用该问题进行检索。
                # 2. 如果没有聊天历史，则直接用原始问题进行检索。
                # 3. 将检索到的文档合并成一个字符串。
                context=RunnableLambda(
                    lambda x: contextualize_q_chain.invoke(x) if x.get("chat_history") else x["question"]
                )
                | retriever
                | _combine_documents
            )
            | QA_PROMPT  # 将组合好的上下文和问题填入最终的问答Prompt
            | llm        # 调用LLM生成答案
        )

        # 最终的链，它将并行地返回AI的回答和溯源文档。
        rag_chain = RunnableMap(
            {
                "answer": qa_chain,
                "source_documents": (
                    # 这部分并行运行，用于获取溯源文档。
                    # 其输入（重构后的问题）与qa_chain中的检索步骤完全相同，以确保一致性。
                    RunnableLambda(
                        lambda x: contextualize_q_chain.invoke(x) if x.get("chat_history") else x["question"]
                    )
                    | retriever
                ),
            }
        )
        logging.info("RAG链创建成功。")
        return rag_chain

    except Exception as e:
        logging.error(f"创建RAG链时出错: {e}", exc_info=True)
        return None

# --- 单例模式入口 ---
# 使用单例模式确保在整个应用生命周期中，RAG链（包括模型）只被加载一次，以节省资源。
rag_chain_instance = None

def get_rag_chain():
    """返回RAG链的单例实例。"""
    global rag_chain_instance
    if rag_chain_instance is None:
        rag_chain_instance = create_rag_chain()
    return rag_chain_instance
