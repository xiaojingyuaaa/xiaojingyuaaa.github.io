from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建一个SQLAlchemy引擎实例。
# `connect_args={"check_same_thread": False}` 这个参数是SQLite特有的，
# 用于允许多线程访问数据库，这在使用FastAPI的异步特性时是必需的。
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建一个SessionLocal类。这个类的每个实例都将是一个独立的数据库会话。
# autocommit=False 和 autoflush=False 确保事务需要手动提交，
# 给予开发者更多的控制权。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个Base类。我们项目中的所有ORM模型都将继承自这个类。
# SQLAlchemy会使用这个基类来发现和映射所有的数据表。
Base = declarative_base()
