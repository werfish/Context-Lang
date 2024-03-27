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
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import ProgrammingError
import os

# Define the base for our models
Base = declarative_base()

# Retrieve the database connection variables from the environment
DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_PORT = os.environ.get('DATABASE_PORT')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

# Construct the PostgreSQL connection string
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_URL}:{DATABASE_PORT}/{DATABASE_NAME}"
)

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Create a SessionLocal class which will serve as a factory for new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_and_create_tables():
    """
    Function that checks if the tables are created and creates them if not.

    It uses the SQLAlchemy Base metadata to reflect and create the tables in
    the database.
    """
    try:
        # Check for existing tables
        if not engine.dialect.has_table(engine, 'some_table_name'):  # Replace 'some_table_name' with an actual table name
            # Create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
        else:
            print("Tables already exist.")
    except ProgrammingError:
        print("An error occurred while checking for tables.")

# Note: You need to ensure that the table name passed to has_table is accurate,
# and that you have defined your SQLAlchemy models with Base before calling check_and_create_tables.
# <CreateDatabaseConnection/>
# <context:DB.PY/>