#<import>MANIFEST.txt<import/>
#<context:DATABASE_SETUP>
# This is the DB intialization file for the project. It contains the database URL for SQLite3 and the base class for the ORM models.
# I need this file to contain that will create the DB if it doesn't exist.
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