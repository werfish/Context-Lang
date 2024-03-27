# Import necessary contexts and setups
#<import>MANIFEST.txt<import/>
#<import>db.py<import/>
#<import>db_models.py<import/>

# Consolidated prompt for generating all ORM queries
#<prompt:GenerateAllORMQueries>
# Utilizing the DB_MODELS_PY generate a set of functions to manage database interactions for all entities. This includes:
# - Creating new instances and adding them to the database.
# - Fetching existing instances by ID or other criteria.
# - Updating instance details in the database.
# - Deleting instances from the database.
# The functions should be designed for the CalculationJob, CalculationResult, and FakeLimitOrder models, ensuring comprehensive database operation capabilities for the application.
# You get the Models code and the db code.
# {DB_MODELS_PY}
# {DB_PY}
# {PROJECT_DESCRIPTION}
#<prompt:GenerateAllORMQueries/>

#<context:QUERIES_PY>
#<GenerateAllORMQueries>
#<GenerateAllORMQueries/>
#<context:QUERIES_PY/>
