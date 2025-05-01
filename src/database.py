from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from dotenv import load_dotenv
import os

load_dotenv()

def get_sql_database():
    # Construct database URL
    db_uri = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:5432/{os.getenv('POSTGRES_DB')}"
    engine = create_engine(db_uri)
    
    return SQLDatabase(engine, include_tables=[
        "student", "subject_score", "subject", "group_schedule",
        "instructor", "room", "department"
    ])
