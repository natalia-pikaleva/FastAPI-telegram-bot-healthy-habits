import asyncio
import csv
import json
import logging
import os
from os import getenv
from dotenv import load_dotenv
from typing import AsyncGenerator, List

import asyncpg
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from main.models import Base, LikeTweet, Media, SubscribedUser, Tweet, User

load_dotenv()

DB_USER = getenv(
    "DB_USER",
)

DB_PASSWORD = getenv(
    "DB_PASSWORD",
)

DB_NAME = getenv(
    "DB_NAME",
)

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@postgres:5432/{DB_NAME}"
)

# engine = create_async_engine(SQLALCHEMY_DATABASE_URI, echo=True)
engine = create_async_engine(SQLALCHEMY_DATABASE_URI)

AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - " "%(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получение асинхронной сессии с базой данных"""
    async with AsyncSessionLocal() as session:
        yield session

async def check_db_exists(db_url: str) -> bool:
    """Проверка существования БД через asyncpg"""
    try:
        conn = await asyncpg.connect(
            user="postgres",
            password="postgres",
            host="postgres",
            database=db_url.split("/")[-1],
        )
        await conn.close()
        return True
    except asyncpg.InvalidCatalogNameError:
        return False
    except Exception as e:
        logger.error(f"Error checking database existence: {e}")
        return False


async def create_database(db_name: str) -> bool:
    """Создание БД с помощью asyncpg"""
    try:
        conn = await asyncpg.connect(
            user="postgres",
            password="postgres",
            host="postgres",
            database="postgres",
        )
        await conn.execute(f"CREATE DATABASE {db_name}")
        await conn.close()
        logger.info(f"Database {db_name} created successfully")
        return True
    except asyncpg.exceptions.DuplicateDatabaseError:
        logger.warning(f"Database {db_name} already exists")
        return True
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False


async def drop_database(db_name) -> None:
    """
    Удаление базы данных.
    """
    try:
        conn = await asyncpg.connect(
            host="postgres", port=5432, user="postgres", password="postgres"
        )
        await conn.execute(f"DROP DATABASE IF EXISTS {db_name};")
        await conn.close()
        logger.info(f"Database {db_name} dropped successfully")
    except asyncpg.exceptions.DatabaseError as e:
        logger.error(f"Failed to drop database: {e}")


async def start_bd(UPLOAD_FOLDER_ABSOLUTE) -> None:
    """
    Создание базы данных при старте
    """
    try:
        # Удаление базы данных, если она существует
        # await drop_database(db_name)
        # await asyncio.sleep(1)

        if not await check_db_exists(SQLALCHEMY_DATABASE_URI):
            logger.info("Database does not exist. Creating...")

            if not await create_database(DB_NAME):
                logger.error("Failed to create database. Exiting.")
                return
            await asyncio.sleep(1)

            global engine
            engine = create_async_engine(SQLALCHEMY_DATABASE_URI, echo=True)

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")

        # async with AsyncSessionLocal() as session:
        #     result = await session.execute(select(User))
        #     users = result.scalars().all()
        #
        #     if not users:
        #         logger.info("Table users is not exists. Start creating")
        #         await insert_users(session)
        #     else:
        #         logger.info("Table users is exists in database")
        #
        #     result = await session.execute(select(Tweet))
        #     tweets = result.scalars().all()
        #     if not tweets:
        #         logger.info("Table tweets is not exists. Start creating")
        #         await insert_tweets_and_likes(session, UPLOAD_FOLDER_ABSOLUTE)
        #     else:
        #         logger.info("Table tweets is exists in database")
        #
        #     result = await session.execute(select(SubscribedUser))
        #     subscribes = result.scalars().all()
        #     if not subscribes:
        #         logger.info("Table subscribes is not exists. Start creating")
        #         await insert_following(session)
        #     else:
        #         logger.info("Table subscribed_users is exists in database")

            await engine.dispose()

    except OperationalError as e:
        logger.error(f"Operational error during database setup: {e}")
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
