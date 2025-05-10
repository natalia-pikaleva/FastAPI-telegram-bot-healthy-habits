import psycopg2
from psycopg2 import OperationalError

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_exists(db_url: str) -> bool:
    """Проверка существования БД через psycopg2 (синхронно)"""
    db_name = db_url.split("/")[-1]
    try:
        # Подключаемся к системной базе 'postgres'
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database="postgres",
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Проверяем, существует ли база данных
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        return exists

    except OperationalError as e:
        logger.error(f"Operational error checking database existence: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking database existence: {e}")
        return False


def create_database() -> bool:
    """Создание БД"""
    try:
        # Подключаемся к системной базе 'postgres'
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database="postgres",
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f'CREATE DATABASE "{DB_NAME}"')
        conn.close()
        logger.info(f"Database {DB_NAME} created successfully")
        return True
    except OperationalError as e:
        logger.error(f"Operational error create database: {e}")
        return False
    except Exception as e:
        logger.error(f"Error create database: {e}")
        return False


def drop_database() -> None:
    """
    Удаление базы данных.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=5432,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f'DROP DATABASE IF EXISTS "{DB_NAME}";')
        conn.close()
        logger.info(f"Database {DB_NAME} dropped successfully")
    except OperationalError as e:
        logger.error(f"Operational error drop database: {e}")
        return False
    except Exception as e:
        logger.error(f"Error drop database: {e}")
        return False
    finally:
        if conn:
            conn.close()


def start_bd() -> None:
    """
    Создание базы данных при старте
    """
    try:
        # drop_database()

        if not check_db_exists(SQLALCHEMY_DATABASE_URI):
            logger.info("Database does not exist. Creating...")
            if not create_database():
                logger.error("Failed to create database. Exiting.")
                return

        global engine, SessionLocal
        engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)  # синхронный движок
        SessionLocal = sessionmaker(bind=engine)

        # Base.metadata.create_all(engine)  # создаём таблицы
        #
        # logger.info("Tables created successfully")

    except OperationalError as e:
        logger.error(f"Operational error during database setup: {e}")
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
