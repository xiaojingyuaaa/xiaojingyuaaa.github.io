import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    UnstructuredFileLoader,
    UnstructuredMarkdownLoader,
    UnstructuredExcelLoader,
)
from langchain.docstore.document import Document

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义文件扩展名到特定加载器的映射
# 这使得我们可以根据文件类型使用最优化的加载器
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
    从指定目录加载所有支持的文档。

    遍历目录下的所有文件，根据文件扩展名选择合适的加载器进行加载。

    Args:
        docs_path (str): 包含文档的目录路径。

    Returns:
        List[Document]: 加载后的Document对象列表。
    """
    path = Path(docs_path)
    if not path.is_dir():
        logging.error(f"路径 {docs_path} 不是一个有效的目录。")
        return []

    loaded_documents = []
    # 递归地遍历目录下的所有文件
    for file_path in path.rglob("*.*"):
        ext = file_path.suffix.lower()
        if ext in LOADER_MAPPING:
            loader_class, loader_args = LOADER_MAPPING[ext]
            try:
                logging.info(f"正在加载文件: {file_path}")
                loader = loader_class(str(file_path), **loader_args)
                # 调用加载器的load方法，并将结果扩展到列表中
                loaded_documents.extend(loader.load())
            except Exception as e:
                logging.error(f"加载文件 {file_path} 失败: {e}", exc_info=True)
        else:
            logging.warning(f"不支持的文件类型: {file_path}，已跳过。")

    logging.info(f"成功加载 {len(loaded_documents)} 个文档块。")
    return loaded_documents
