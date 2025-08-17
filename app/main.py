import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import endpoints
from app.db.database import Base, engine

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_db_and_tables():
    """
    创建数据库和所有在ORM模型中定义的表。
    这个函数会在应用启动时被调用。
    """
    logging.info("正在创建数据库和表...")
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("数据库和表已成功创建。")
    except Exception as e:
        logging.error(f"创建数据库表时出错: {e}", exc_info=True)
        raise

# 创建FastAPI应用实例
app = FastAPI(
    title="企业级RAG智能客服API",
    description="一个为公司内部智能客服助手提供支持的API，由RAG技术驱动。",
    version="1.1.0", # 版本升级
)

# 应用启动时执行的事件处理器
@app.on_event("startup")
def on_startup():
    """
    应用启动时的事件处理函数。
    """
    create_db_and_tables()

# CORS（跨域资源共享）策略现在由Nginx反向代理处理。
# 因此，不再需要在FastAPI应用层添加CORS中间件。
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# 包含API路由
app.include_router(endpoints.router, prefix="/api", tags=["聊天与会话管理"])

# 用于健康检查的根节点
@app.get("/", tags=["健康检查"])
def read_root():
    """
    根节点，用于检查服务是否正在运行。
    """
    return {"status": "ok", "message": "欢迎使用企业级RAG智能客服API!"}
