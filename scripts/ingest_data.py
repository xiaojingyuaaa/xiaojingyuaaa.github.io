import sys
import os
import logging

# 将项目根目录添加到Python的模块搜索路径中
# 这使得该脚本可以作为独立脚本运行时，能够正确地导入'app'目录下的模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.rag.loader import load_documents
from app.rag.vector_store import create_vector_store
from app.core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    数据灌输主函数。
    - 从配置文件中指定的源目录加载文档。
    - 从加载的文档创建并保存向量数据库。
    """
    logging.info("开始执行数据灌输流程...")

    # 步骤 1: 从配置指定的路径加载文档
    logging.info(f"正在从路径加载文档: {settings.DOCS_PATH}")
    try:
        documents = load_documents(settings.DOCS_PATH)
        if not documents:
            logging.warning("未能加载任何文档。请检查DOCS_PATH及其内容是否正确。")
            return
        logging.info(f"成功加载 {len(documents)} 个文档块。")
    except Exception as e:
        logging.error(f"文档加载过程中发生错误: {e}", exc_info=True)
        return

    # 步骤 2: 创建并保存向量数据库
    try:
        create_vector_store(documents)
    except Exception as e:
        logging.error(f"创建向量数据库过程中发生错误: {e}", exc_info=True)
        return

    logging.info("数据灌输流程成功完成。")

if __name__ == "__main__":
    # 要运行此脚本，请在项目根目录下执行 `python scripts/ingest_data.py`
    # 或者在使用Docker时，执行 `docker-compose exec backend python scripts/ingest_data.py`
    main()
