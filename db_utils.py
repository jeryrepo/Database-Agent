import os
import re
import sqlite3
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain_community.utilities.sql_database import SQLDatabase

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_engine_for_chinook_db():
    url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
    response = requests.get(url)
    sql_script = response.text
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    return create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

def get_sql_db():
    engine = get_engine_for_chinook_db()
    return SQLDatabase(engine)

def fix_common_sql_typos(query: str) -> str:
    # Automatically fix common SQL formatting issues
    query = re.sub(r'LIMIT(\d)', r'LIMIT \1', query, flags=re.IGNORECASE)
    return query
