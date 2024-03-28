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
# models.py
# We need to import necessary components from sqlalchemy
from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import json

# Import Base from db.py (assuming you are in the same package and db.py is a module)
from .db import Base  

# SQLAlchemy models based on context provided

#<GenerateORMModels>

# CALCULATION_JOB_MODEL
class CalculationJob(Base):
    __tablename__ = 'calculation_jobs'

    # Using PostgreSQL UUID type for job_id
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    period = Column(Integer)
    standard_deviation_multiplier = Column(Float)
    status = Column(Enum("pending", "processing", "completed", "failed", name="status_enum"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relationship to connect with CalculationResult
    results = relationship("CalculationResult", back_populates='job')

# CALCULATION_RESULT_MODEL
class CalculationResult(Base):
    __tablename__ = 'calculation_results'

    # Using PostgreSQL UUID type for result_id
    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('calculation_jobs.job_id'))
    upper_band = Column(String)  # Using JSON as String for compatibility
    middle_band = Column(String)
    lower_band = Column(String)
    calculated_at = Column(DateTime)

    # Relationship to connect with CalculationJob
    job = relationship("CalculationJob", back_populates='results')

# FAKE_LIMIT_ORDER_MODEL
class FakeLimitOrder(Base):
    __tablename__ = 'fake_limit_orders'

    # Using PostgreSQL UUID type for order_id
    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, default="limit")
    price = Column(Numeric(10, 2))
    quantity = Column(Numeric(10, 2))
    direction = Column(Enum("buy", "sell", name="direction_enum"))
    status = Column(Enum("open", "cancelled", "executed", name="status_enum"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

#<GenerateORMModels/>

# After defining the models, we need to call init_db from db.py to ensure the tables are created.
# We'll invoke this function at the appropriate time when starting the application.

# db.py modification to include models import
# Please make sure to uncomment the init_db() call when you are ready to create the tables.
# from .models import CalculationJob, CalculationResult, FakeLimitOrder  # Uncomment this on actual db.py file
# init_db()  # Uncomment this when initiating your application to create tables

# Note: The JSON type for the Bollinger Bands is returned as a string type in this ORM model implementation.
# This is due to SQLite not natively supporting JSON types.
# In production, for PostgreSQL, we might use the JSON type from SQLAlchemy.
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>