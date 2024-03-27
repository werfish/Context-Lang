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
from typing import List, Optional
from sqlalchemy.orm import Session
from .db_models import CalculationJob, CalculationResult, FakeLimitOrder
from .db import get_db

# CRUD operations for CalculationJob
class CalculationJobCRUD:
    @staticmethod
    def create_calculation_job(db: Session, job_data: dict) -> CalculationJob:
        job = CalculationJob(**job_data)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def get_calculation_job_by_id(db: Session, job_id: int) -> Optional[CalculationJob]:
        return db.query(CalculationJob).filter(CalculationJob.id == job_id).first()
    
    @staticmethod
    def update_calculation_job(db: Session, job_id: int, update_data: dict) -> CalculationJob:
        job = db.query(CalculationJob).filter(CalculationJob.id == job_id).first()
        if job:
            for key, value in update_data.items():
                setattr(job, key, value)
            db.commit()
            db.refresh(job)
        return job
    
    @staticmethod
    def delete_calculation_job(db: Session, job_id: int):
        db.query(CalculationJob).filter(CalculationJob.id == job_id).delete()
        db.commit()

# CRUD operations for CalculationResult
class CalculationResultCRUD:
    # Similar CRUD methods for CalculationResult, specific to the model's fields and use cases.

# CRUD operations for FakeLimitOrder
class FakeLimitOrderCRUD:
    # Similar CRUD methods for FakeLimitOrder, specific to the model's fields and use cases.

#<GenerateAllORMQueries/>
#<context:QUERIES_PY/>
