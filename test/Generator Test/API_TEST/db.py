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
# <CreateDatabaseConnection/>
# <context:DB_PY/>