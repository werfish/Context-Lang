#<import>MANIFEST.txt<import/>
#<context:DATABASE_SETUP>
# This is the DB intialization file for the project. 
# It contains the database URL for SQLite3 and the base class for the ORM models.
# I need this file to contain a function that will create the DB if it doesn't exist.
# and create all the tables based on the models defined in db_models.py.
# THE MODELS WILL BE WRITTEN AFTER THIS FILE, SO THE FUNCTION WILL BE CALLED IN THE MODELS FILE!!
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
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import os

# Define the path for SQLite3 database. 
DATABASE_URL = "sqlite:///./database.db"
Base = declarative_base()  # The base class to create models

# Create an engine that the Session will use for connection resources.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a custom SessionLocal class that will establish the actual sessions later.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_database():
    
    
    
    
    
    
    
    
    
    # Check for the existence of SQLite3 database file and create it if not exists
    if not os.path.exists('./database.db'):
        # Create the database file
        try:
            conn = engine.connect()
            conn.close()
        except OperationalError as e:
            print(f"An error occurred while creating the database: {e}")
    
    # Import the models and create all tables
    # This import must be here to avoid circular imports as it relies on the Base and engine defined above
    from db_models import Base  # Import the Base from db_models.py
    
    # Use Base to create all tables in the database.
    Base.metadata.create_all(bind=engine)

# This function must be called after defining all models in db_models.py to ensure tables creation

# Don't forget to run this function in your `db_models.py` file to create/update database tables:
# from database_setup import create_database
# create_database()
# <CreateDatabaseConnection/>
# <context:DB_PY/>