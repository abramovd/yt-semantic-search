import mariadb
from sqlmodel import SQLModel, create_engine
import os
from functools import lru_cache
username = os.getenv("DB_USER", "app_user")
password = os.getenv("DB_PASSWORD", "Password123!")
host = os.getenv("DB_HOST", "127.0.0.1")
port = int(os.getenv("DB_PORT", "3306"))
database = os.getenv("DB_NAME", "semantic_search")


def sqlmodel_on_startup():
    mariadb_url = f"mariadb+mariadbconnector://{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(mariadb_url, echo=True)
    SQLModel.metadata.create_all(engine)

@lru_cache
def native_connection():
    conn = mariadb.connect(
       host=host,
       port=port,
       user=username,
       password=password
   )
    return conn

def native_on_startup():
    conn = native_connection()
    cur = conn.cursor()
    cur.execute(f"""
       CREATE DATABASE IF NOT EXISTS {database};
       """)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {database}.documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            meta JSON NOT NULL
        );
        """)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {database}.chunks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            start_ts INT NOT NULL,
            end_ts INT NOT NULL,
            text LONGTEXT NOT NULL,
            document_id INT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id),
            embedding VECTOR(384) NOT NULL,
            VECTOR INDEX (embedding)
        );
        """)


def create_db_and_tables():
    native_on_startup()