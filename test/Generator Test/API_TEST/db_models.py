# # Import global project settings and libraries
# <import>MANIFEST.txt<import/>
# <import>DataModel.txt<import/>
# <import>db.py<import/>

# # Prompt for generating SQLAlchemy models
# <prompt:GenerateORMModels>
# Please generate SQLAlchemy ORM models based on the project descriptions and specifications provided. This should include models for calculation jobs, calculation results, and fake limit orders as detailed in the project documentation.
# database setup is in db.py file.
# {PROJECT_DESCRIPTION} 
# {LIBRARIES} 
# {DB.PY}
# <prompt:GenerateORMModels/>

# <context:DB_MODELS_PY>
# <GenerateORMModels>
# {DB.PY}

from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create the base class from which all mapped classes should inherit
Base = declarative_base()

class CalculationJob(Base):
    __tablename__ = 'calculation_jobs'

    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, index=True, nullable=False, default='BTC/USDT')
    timeframe = Column(String, default='1S')  # 1-second timeframe
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, index=True, default='submitted') # Possible statuses: submitted, processing, completed, failed
    results = relationship("CalculationResult", back_populates="job")  # One-to-Many relationship

class CalculationResult(Base):
    __tablename__ = 'calculation_results'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('calculation_jobs.id'), index=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    upper_band = Column(Float)
    lower_band = Column(Float)
    moving_average = Column(Float)
    job = relationship("CalculationJob", back_populates="results")  # Many-to-One relationship

class FakeLimitOrder(Base):
    __tablename__ = 'fake_limit_orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)  # Assuming there is a users table
    pair = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    side = Column(String, default='buy')  # 'buy' or 'sell'
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# This function can be used to create all tables in the database
def create_all_tables(engine):
    Base.metadata.create_all(engine)

# Other database setup code, such as engine creation, session management, etc., should also be included here.
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>