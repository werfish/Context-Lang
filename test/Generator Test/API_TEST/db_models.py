# # Import global project settings and libraries
# <import>MANIFEST.txt<import/>
# <import>db.py<import/>
# <file:DataModel>DataModel.txt<file:DataModel/>

# # Prompt for generating SQLAlchemy models
# <prompt:GenerateORMModels>
# Please generate SQLAlchemy ORM models based on the project descriptions and specifications provided. 
# This should include models for calculation jobs, calculation results, and fake limit orders as detailed in the project documentation.
# db.py file contains the database engine and session setup and has a function to create the database tables if they don't exist.
# Please call this function after models are created to ensure the tables are created in the database.
# {PROJECT_DESCRIPTION} 
# {LIBRARIES} 
# {DataModel}
# {DB_PY}
# <prompt:GenerateORMModels/>

# <context:DB_MODELS_PY>
# <GenerateORMModels>
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Enum, JSON, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from db import Base  # Import the base class for the ORM
import uuid

# Enum for the job status
class JobStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

# Enum for the fake limit order status
class OrderStatus(enum.Enum):
    open = "open"
    cancelled = "cancelled"
    executed = "executed"

# Enum for the fake limit order direction
class OrderDirection(enum.Enum):
    buy = "buy"
    sell = "sell"

# CalculationJob model
class CalculationJob(Base):
    __tablename__ = 'calculation_jobs'
    
    # Fields
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    period = Column(Integer)
    standard_deviation_multiplier = Column(Float)
    status = Column(Enum(JobStatus))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # Relationships
    calculation_results = relationship('CalculationResult', back_populates='calculation_job')

# CalculationResult model
class CalculationResult(Base):
    __tablename__ = 'calculation_results'
    
    # Fields
    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('calculation_jobs.job_id'))
    upper_band = Column(JSON)
    middle_band = Column(JSON)
    lower_band = Column(JSON)
    calculated_at = Column(DateTime)
    
    # Relationships
    calculation_job = relationship('CalculationJob', back_populates='calculation_results')

# FakeLimitOrder model
class FakeLimitOrder(Base):
    __tablename__ = 'fake_limit_orders'
    
    # Fields
    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, default="limit")
    price = Column(DECIMAL)
    quantity = Column(DECIMAL)
    direction = Column(Enum(OrderDirection))
    status = Column(Enum(OrderStatus))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# this will be executed to create the database tables
def create_tables():
    from db import init_db
    init_db()

create_tables()
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>