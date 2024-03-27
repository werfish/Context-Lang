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
# {CreateDatabaseConnection}
# {DB.PY}
# <prompt:GenerateORMModels/>

# <context:DB_MODELS_PY>
# <GenerateORMModels>
from sqlalchemy import Column, Integer, Float, String, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.future import select

# Assuming you have a config file or environment variable management for the DB URI.
# from config import SQLALCHEMY_DATABASE_URI
DATABASE_URI = "sqlite:///./test.db"  # Placeholder, replace with actual DB URI

Base = declarative_base()

# Database connection setup
engine = create_engine(DATABASE_URI, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Models
class CalculationJob(Base):
    __tablename__ = 'calculation_jobs'
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")
    btc_usdt_pair = Column(String, index=True)
    # additional fields as necessary
    
    # Relationship to calculate results
    results = relationship("CalculationResult", back_populates="job")

class CalculationResult(Base):
    __tablename__ = 'calculation_results'
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('calculation_jobs.id'))
    value = Column(Float)  # Change to appropriate field type
    # additional fields as necessary
    
    # Relationship to calculation jobs
    job = relationship("CalculationJob", back_populates="results")
    
class FakeLimitOrder(Base):
    __tablename__ = 'fake_limit_orders'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # or a ForeignKey to a User model, if exists
    price = Column(Float)
    amount = Column(Float)
    side = Column(String)
    # additional fields as necessary

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# <GenerateORMModels/>
# <context:DB_MODELS_PY/>