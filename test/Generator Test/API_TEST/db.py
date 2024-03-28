#<import>MANIFEST.txt<import/>
#<context:DATABASE_SETUP>
# This is the DB intialization file for the project. 
# It contains the database URL for SQLite3 and the base class for the ORM models.
# I need this file to contain a function that will create the DB if it doesn't exist.
# and create all the tables based on the models defined in db_models.py.
# it will be run in models.py to ensure the database is created and the tables are created.
# The database needs to have a name database.db and be located in the root directory of the project.
#<context:DATABASE_SETUP/>

#<prompt:CreateDatabaseConnection>
# Based on the DATABASE_SETUP context, generate the SQLAlchemy database connection code, including engine creation and SessionLocal definition.
# {DATABASE_SETUP}
# {LIBRARIES}
# {INFRASTRUCTURE}
#<prompt:CreateDatabaseConnection/>

# <context:DB_PY>
# <CreateDatabaseConnection>
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Dependency
from . import db_models  # assuming db_models is a module in the current package

# Constants for your database setup
DATABASE_NAME = 'database.db'
DATABASE_URL = f'sqlite:///{DATABASE_NAME}'

# Ensure the database directory exists. Create it if it doesn't.
if not os.path.exists(DATABASE_NAME):
    open(DATABASE_NAME, 'a').close()

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured "SessionLocal" class which will serve as a factory for new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

def init_db():
    """
    Create all tables in the database.
    This is equivalent to "Create Database" in other SQL databases,
    given SQLite doesn't separate the concept of database create from table create.
    """
    import db_models  # Import all the models
    Base.metadata.create_all(bind=engine)

# <CreateDatabaseConnection/>
# <context:DB_PY/>