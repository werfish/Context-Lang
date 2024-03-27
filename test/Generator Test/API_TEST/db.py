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

# <context:DB_PY>
# <CreateDatabaseConnection>
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from . import models # Import your models where your SQLAlchemy ORM tables are defined

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

# Create an engine instance
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your models
Base = declarative_base()

# Function to create tables if they don't exist
def create_tables():
    if not engine.dialect.has_table(engine, 'table_name'):  # Replace 'table_name' with your table name
        Base.metadata.create_all(bind=engine)
# <CreateDatabaseConnection/>
# <context:DB_PY/>