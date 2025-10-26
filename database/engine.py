import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs


# SQLAlchemy 2.0 Base for declarative models (used by database.models and run.py)
class Base(AsyncAttrs, DeclarativeBase):
    pass


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'database.db')


if os.path.exists('/.dockerenv'):
    DATABASE_URL = f'sqlite+aiosqlite:////app/database/database.db'
else:
    DATABASE_URL = f'sqlite+aiosqlite:///{DB_PATH}'

async_engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


