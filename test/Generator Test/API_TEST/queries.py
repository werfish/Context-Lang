# Import necessary contexts and setups
#<import>MANIFEST.txt<import/>
#<import>db.py<import/>
#<import>db_models.py<import/>

# Consolidated prompt for generating all ORM queries
#<prompt:GenerateAllORMQueries>
# Utilizing the DB_MODELS_PY and context, generate a set of functions to manage database interactions for all entities. This includes:
# - Creating new instances and adding them to the database.
# - Fetching existing instances by ID or other criteria.
# - Updating instance details in the database.
# - Deleting instances from the database.
# The functions should be designed for the CalculationJob, CalculationResult, and FakeLimitOrder models, ensuring comprehensive database operation capabilities for the application.
# {DB_MODELS_PY}
# {DB.PY}
# {PROJECT_DESCRIPTION}
#<prompt:GenerateAllORMQueries/>

#<context:QUERIES_PY>
#<GenerateAllORMQueries>
- `create_calculation_job`
- `get_calculation_job_by_id`
- `update_calculation_job`
- `delete_calculation_job`
- `create_calculation_result`
- `get_calculation_result_by_criteria`
- `update_calculation_result`
- `delete_calculation_result`
- `create_fake_limit_order`
- `get_fake_limit_order_by_criteria`
- `update_fake_limit_order`
- `delete_fake_limit_order`
#<GenerateAllORMQueries/>
#<context:QUERIES_PY/>
