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
# <ORMDatabaseInteractions>
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from .db_models import CalculationJob, CalculationResult, FakeLimitOrder
import datetime

# Create a new calculation job
def create_calculation_job(db: Session, start_time, end_time, period, std_dev_multiplier):
    new_job = CalculationJob(
        start_time=start_time,
        end_time=end_time,
        period=period,
        standard_deviation_multiplier=std_dev_multiplier,
        status='pending',
        created_at=datetime.datetime.now()
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

# Fetch a calculation job by ID
def get_calculation_job(db: Session, job_id: str):
    return db.query(CalculationJob).filter(CalculationJob.job_id == job_id).one_or_none()

# Update calculation job details
def update_calculation_job(db: Session, job_id: str, status: str):
    job = db.query(CalculationJob).filter(CalculationJob.job_id == job_id).one_or_none()
    if job:
        job.status = status
        job.updated_at = datetime.datetime.now()
        db.commit()
        return job
    return None

# Delete a calculation job
def delete_calculation_job(db: Session, job_id: str):
    job = db.query(CalculationJob).filter(CalculationJob.job_id == job_id).one_or_none()
    if job:
        db.delete(job)
        db.commit()

# Create a new calculation result
def create_calculation_result(db: Session, job_id: str, upper_band, middle_band, lower_band):
    new_result = CalculationResult(
        job_id=job_id,
        upper_band=json.dumps(upper_band),
        middle_band=json.dumps(middle_band),
        lower_band=json.dumps(lower_band),
        calculated_at=datetime.datetime.now()
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    return new_result

# Fetch calculation results for a job
def get_calculation_result(db: Session, job_id: str):
    return db.query(CalculationResult).filter(CalculationResult.job_id == job_id).all()

# Submit a new fake limit order
def create_fake_limit_order(db: Session, order_type, price, quantity, direction):
    new_order = FakeLimitOrder(
        type=order_type,
        price=price,
        quantity=quantity,
        direction=direction,
        status='open',
        created_at=datetime.datetime.now()
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

# Fetch all fake limit orders
def list_all_fake_orders(db: Session):
    return db.query(FakeLimitOrder).all()

# Fetch a single fake limit order
def get_fake_limit_order(db: Session, order_id: str):
    return db.query(FakeLimitOrder).filter(FakeLimitOrder.order_id == order_id).one_or_none()

# Update fake limit order details
def update_fake_limit_order(db: Session, order_id: str, price=None, quantity=None):
    order = db.query(FakeLimitOrder).filter(FakeLimitOrder.order_id == order_id).one_or_none()
    if order:
        if price is not None:
            order.price = price
        if quantity is not None:
            order.quantity = quantity
        order.updated_at = datetime.datetime.now()
        db.commit()
        return order
    return None

# Delete a fake limit order
def delete_fake_limit_order(db: Session, order_id: str):
    order = db.query(FakeLimitOrder).filter(FakeLimitOrder.order_id == order_id).one_or_none()
    if order:
        db.delete(order)
        db.commit()

# <ORMDatabaseInteractions/>
#<GenerateAllORMQueries/>
#<context:QUERIES_PY/>
