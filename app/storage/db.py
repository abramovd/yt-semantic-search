import mariadb
from functools import lru_cache

from app import config

@lru_cache
def native_connection():
    conn = mariadb.connect(
       host=config.DB_HOST,
       port=config.DB_PORT,
       user=config.DB_USERNAME,
       password=config.DB_PASSWORD
   )
    return conn

def drop_database():
    conn = native_connection()
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {config.DB_NAME};")

def native_on_startup():
    conn = native_connection()
    cur = conn.cursor()
       
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME};")
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.DB_NAME}.documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(512) NOT NULL,
            url VARCHAR(256) NOT NULL,
            created_at DATETIME NOT NULL,
            meta JSON NOT NULL
        );
    """)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {config.DB_NAME}.chunks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chunk_index INT NOT NULL,
            start_ts FLOAT NOT NULL,
            end_ts FLOAT NOT NULL,
            text LONGTEXT NOT NULL,
            document_id INT NOT NULL,
            FOREIGN KEY (document_id) REFERENCES documents(id),
            embedding VECTOR(384) NOT NULL,
            VECTOR INDEX (embedding)
        );
    """)


def create_db_and_tables(drop_db_first: bool = False):
    if drop_db_first:
        drop_database()
        
    native_on_startup()
    