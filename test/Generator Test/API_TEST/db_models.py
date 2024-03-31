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
from sqlalchemy import Column,Integer, DateTime, Enum, Float, ForeignKey, JSON, String
from sqlalchemy.dialects.sqlite import DECIMAL
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum
from db import Base, create_database

# Enums for status fields
class CalculationJobStatus(enum.Enum):
    pending = 'pending'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'

class FakeLimitOrderStatus(enum.Enum):
    open = 'open'
    cancelled = 'cancelled'
    executed = 'executed'

class FakeLimitOrderDirection(enum.Enum):
    buy = 'buy'
    sell = 'sell'

class CalculationJob(Base):
    __tablename__ = 'calculation_jobs'
    job_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    period = Column(Integer)
    standard_deviation_multiplier = Column(Float)
    status = Column(Enum(CalculationJobStatus))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # Relationship to CalculationResult
    results = relationship("CalculationResult", back_populates="job")
    
class CalculationResult(Base):
    __tablename__ = 'calculation_results'
    result_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    job_id = Column(String, ForeignKey('calculation_jobs.job_id'))
    upper_band = Column(JSON)
    middle_band = Column(JSON)
    lower_band = Column(JSON)
    calculated_at = Column(DateTime)
    
    # Relationship to CalculationJob
    job = relationship("CalculationJob", back_populates="results")

class FakeLimitOrder(Base):
    __tablename__ = 'fake_limit_orders'
    order_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    type = Column(String, default='limit')
    price = Column(DECIMAL)
    quantity = Column(DECIMAL)
    direction = Column(Enum(FakeLimitOrderDirection))
    status = Column(Enum(FakeLimitOrderStatus))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# Uncomment and use the following class if storing price data is required for your application.
class PriceData(Base):
    __tablename__ = 'price_data'
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    timestamp = Column(DateTime)
    price = Column(DECIMAL)
    volume = Column(DECIMAL, nullable=True)

# Ensure the database and tables are created after defining the models.
create_database()
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>