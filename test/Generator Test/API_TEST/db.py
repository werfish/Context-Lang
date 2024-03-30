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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# DATABASE URL
DATABASE_URL = "sqlite:///./database.db"

# ENGINE CREATION
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# SESSION LOCAL DEFINITION
# This class will allow us to create a session in each request
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# BASE CLASS FOR ORM MODELS
Base = declarative_base()

# DB INITIALIZATION FUNCTION
def init_db():
    # This function checks for the existence of the database and creates the tables if they do not exist.
    
    # Import all the models
    import db_models
    
    # Ensure the SQLite database file exists
    if not os.path.exists("./database.db"):
        # If not, create the SQLite file
        open("./database.db", 'a').close()
    
    # Create all tables in the database by using metadata
    Base.metadata.create_all(bind=engine)

# The init_db function will be called inside the db_models.py once all models are defined.
# <CreateDatabaseConnection/>
# <context:DB_PY/>