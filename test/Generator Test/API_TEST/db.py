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
# <CreateDatabaseConnection/>
# <context:DB_PY/>