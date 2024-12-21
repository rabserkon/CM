from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .models import Base

# Подключение к PostgreSQL через Docker
DATABASE_URL = "postgresql://admin:admin@localhost:5432/materials"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Создаёт таблицы в базе данных."""
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        raise RuntimeError(f"Ошибка при инициализации базы данных: {e}")

def check_connection():
    """Проверяет подключение к базе данных."""
    try:
        connection = engine.connect()
        connection.close()
        return True
    except OperationalError as e:
        return False, str(e)