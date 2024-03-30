# Import necessary contexts and setups
#<import>MANIFEST.txt<import/>
#<import>db.py<import/>
#<import>db_models.py<import/>
#<file:Endpoints>Endpoints.txt<file:Endpoints/>

# Consolidated prompt for generating all ORM queries
#<prompt:GenerateAllORMQueries>
# Utilizing the DB_MODELS_PY generate a set of functions to manage database interactions for all entities. This includes:
# - Creating new instances and adding them to the database.
# - Fetching existing instances by ID or other criteria.
# - Updating instance details in the database.
# - Deleting instances from the database.
# The functions should be designed for the CalculationJob, CalculationResult, and FakeLimitOrder models, ensuring comprehensive database operation capabilities for the application.
# You get the Models code and the db code.
# I will also give you the description of the project and
# Endpoint descriptions so you know what ORM queries to generate so they are usefull.
# {PROJECT_DESCRIPTION}
# {Endpoints}
# {DB_PY}
# {DB_MODELS_PY}
#<prompt:GenerateAllORMQueries/>

#<context:QUERIES_PY>
#<GenerateAllORMQueries>
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db_models import CalculationJob, CalculationResult, FakeLimitOrder, JobStatus, OrderDirection, OrderStatus
from typing import List, Optional
from uuid import UUID
import datetime


# CalculationJob Operations

def create_calculation_job(db: Session, start_time: datetime.datetime, end_time: datetime.datetime, period: int, std_multiplier: float) -> CalculationJob:
    job = CalculationJob(
        start_time=start_time, 
        end_time=end_time, 
        period=period, 
        standard_deviation_multiplier=std_multiplier,
        status=JobStatus.pending,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_calculation_job(db: Session, job_id: UUID) -> CalculationJob:
    return db.query(CalculationJob).filter(CalculationJob.job_id == job_id).first()

def update_calculation_job(db: Session, job_id: UUID, status: JobStatus) -> CalculationJob:
    job = db.query(CalculationJob).filter(CalculationJob.job_id == job_id).first()
    if job:
        job.status = status
        job.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(job)
    return job

def delete_calculation_job(db: Session, job_id: UUID) -> None:
    db.query(CalculationJob).filter(CalculationJob.job_id == job_id).delete()
    db.commit()


# CalculationResult Operations

def create_calculation_result(db: Session, job_id: UUID, upper_band: List, middle_band: List, lower_band: List) -> CalculationResult:
    result = CalculationResult(
        job_id=job_id, 
        upper_band=upper_band, 
        middle_band=middle_band, 
        lower_band=lower_band,
        calculated_at=datetime.datetime.utcnow()
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

def get_calculation_result(db: Session, job_id: UUID) -> CalculationResult:
    return db.query(CalculationResult).filter(CalculationResult.job_id == job_id).first()


# FakeLimitOrder Operations

def create_fake_limit_order(db: Session, price: float, quantity: float, direction: OrderDirection) -> FakeLimitOrder:
    order = FakeLimitOrder(
        price=price, 
        quantity=quantity, 
        direction=direction, 
        status=OrderStatus.open,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_fake_limit_order(db: Session, order_id: UUID) -> FakeLimitOrder:
    return db.query(FakeLimitOrder).filter(FakeLimitOrder.order_id == order_id).first()

def update_fake_limit_order(db: Session, order_id: UUID, price: Optional[float], quantity: Optional[float]) -> FakeLimitOrder:
    order = db.query(FakeLimitOrder).filter(FakeLimitOrder.order_id == order_id).first()
    if order:
        if price is not None:
            order.price = price
        if quantity is not None:
            order.quantity = quantity
        order.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order

def delete_fake_limit_order(db: Session, order_id: UUID) -> None:
    db.query(FakeLimitOrder).filter(FakeLimitOrder.order_id == order_id).delete()
    db.commit()

def list_all_fake_limit_orders(db: Session) -> List[FakeLimitOrder]:
    return db.query(FakeLimitOrder).all()
#<GenerateAllORMQueries/>
#<context:QUERIES_PY/>
