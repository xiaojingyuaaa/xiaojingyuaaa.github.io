from typing import Generator
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    一个FastAPI依赖项，用于提供SQLAlchemy的数据库会话。

    它通过try...finally块确保数据库会话在请求处理完毕后总是被关闭，
    即使在处理过程中发生了错误。

    Yields:
        Generator[Session, None, None]: 一个SQLAlchemy会话生成器。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
