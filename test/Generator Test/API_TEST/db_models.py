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
# {DB_PY}
# <prompt:GenerateORMModels/>

# <context:DB_MODELS_PY>
# <GenerateORMModels>
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class CalculationJob(Base):
    __tablename__ = 'calculation_jobs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)  # Assuming you have a user model
    symbol = Column(String(10), nullable=False, default='BTC/USDT')
    timeframe = Column(String(10), nullable=False, default='1s')
    status = Column(String(20), nullable=False, default='pending')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    results = relationship("CalculationResult", back_populates="job")
    
class CalculationResult(Base):
    __tablename__ = 'calculation_results'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('calculation_jobs.id'), nullable=False)
    upper_band = Column(Float, nullable=False)
    middle_band = Column(Float, nullable=False)
    lower_band = Column(Float, nullable=False)
    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    job = relationship("CalculationJob", back_populates="results")
    
class FakeLimitOrder(Base):
    __tablename__ = 'fake_limit_orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)  # Assuming you have a user model
    symbol = Column(String(10), nullable=False, default='BTC/USDT')
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    side = Column(String(10), nullable=False)  # 'buy' or 'sell'
    status = Column(String(20), nullable=False, default='open')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Place additional necessary code for database setup here, like engine creation
# and session management based on the framework and library specifications mentioned.
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>