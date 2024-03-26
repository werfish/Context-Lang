#<import>MANIFEST.txt<import/>
#<context:DATABASE_SETUP>
# This context describes the setup for a PostgreSQL database connection using SQLAlchemy in a FastAPI application. It should include creating the database URI from environment variables and initializing the SQLAlchemy engine and session.
# Please assume that the environment variables for the database connection are already defined.
# Please create a function wich checks whether any tables are created or not. 
# if not the function should create the tables. This function will be run in main.py on startup.
#<context:DATABASE_SETUP/>

#<prompt:CreateDatabaseConnection>
# Based on the DATABASE_SETUP context, generate the SQLAlchemy database connection code, including engine creation and SessionLocal definition.
# {DATABASE_SETUP}
#<prompt:CreateDatabaseConnection/>

# <context:DB.PY>
# <CreateDatabaseConnection>
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database
import os

# Define the database URL from environment variables
DATABASE_URL = (
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}"
    f"@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a scoped session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Declare the Base class for declarative table definitions
Base = declarative_base()

def check_and_create_tables():
    """
    Check if any tables are created, if not creates the tables.
    Run this function in main.py on startup.
    """
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Check for tables and create if they're not existing
    if not engine.dialect.has_table(engine, 'example_table'):  # Replace 'example_table' with a relevant table name
        Base.metadata.create_all(bind=engine)
        print("Tables created.")
    else:
        print("Tables already exist, skipping creation.")
# <CreateDatabaseConnection/>
# <context:DB.PY/>