# <file:MANIFEST>MANIFEST.txt<file:MANIFEST/>
# <file:ENDPOINTS>Endpoints.txt<file:ENDPOINTS/>
# <import:DB_MODELS_PY>db_models.py<import:DB_MODELS_PY/>
# <import:QUERIES_PY>queries.py<import:QUERIES_PY/>
# <import:PydanticModels>pydantic_models.py<import:PydanticModels/>
# <import:DB_PY>db.py<import:DB_PY/>


# <context:MAIN_REQUIREMENTS>
# Requirements for this codefile (main.py) are as follows:
# 1. Make all the correct imports based on the manifest.
# 2. Initialize FastAPI, Logging etc based on the manifest.
# 3. Implement all the endpoints based on the ENDPOINTS design file
# data model, pydantic models and ORM Querrires provided.
# 4. Please use the dependency injection approach for the endpoints
# 5. Use appriopriate error handling for each endpoint.
# 6. I want to execute this file with Python main.py, so intialize everything inside the code

# <context:MAIN_REQUIREMENTS/>

# <prompt:CreateMainFastApiFile>
# Please write the code according to the main requirements.
# For context you get the MANIFEST with high level project description,
# the db models file, the queries file and the db file.
# Also I will give you the initial design for the endpoints.
# REMEMBER THAT THIS FILE NEEDS TO RUN WITH "PYTHON main.py"
# {MANIFEST}
# {QUERIES_PY}
# {DB_MODELS_PY}
# {DB_PY}
# {PydanticModels}
# {ENDPOINTS}
# <prompt:CreateMainFastApiFile/>

# <context:MainEndpoints>
# <CreateMainFastApiFile>
from fastapi import FastAPI, HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from db_models import Base, PriceData
from pydantic_models import (
    CalculationJobCreate, CalculationJobDetailOutput, CalculationJobOutput,
    FakeLimitOrderCreate, FakeLimitOrderOutput
)
from queries import DatabaseManager
import uvicorn
import numpy as np
from decimal import Decimal, getcontext

getcontext().prec = 10

# Dependency for getting the database session for each request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.post("/calculate-bollinger", response_model=CalculationJobOutput)
def calculate_bollinger(data: CalculationJobCreate, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    job = db_manager.create_calculation_job(
        start_time=data.start_time, 
        end_time=data.end_time, 
        period=data.period, 
        standard_deviation_multiplier=Decimal(data.standard_deviation_multiplier)
    )

    # Fetch price data for the specified period
    # Use the optimized method to fetch price data
    price_data = db_manager.get_price_data_for_period(data.start_time, data.end_time, data.period)

    # Ensure there's enough data to calculate Bollinger Bands
    prices = [Decimal(price[0]) for price in price_data]  # Convert prices to Decimal

    if len(prices) >= data.period:
        # Convert list of Decimal prices to numpy array of floats for calculation
        # Note: Numpy does not support Decimal directly, so precision might be slightly affected
        prices_floats = np.array([float(price) for price in prices])

        # Calculate SMA for the specified period
        sma = np.mean(prices_floats[-data.period:])
        
        # Calculate standard deviation for the specified period
        std_dev = np.std(prices_floats[-data.period:])
        
        # Convert back to Decimal for precise arithmetic operations
        sma_decimal = Decimal(sma)
        std_dev_decimal = Decimal(std_dev)

        # Calculate Bollinger Bands
        upper_band = sma_decimal + (std_dev_decimal * Decimal(data.standard_deviation_multiplier))
        lower_band = sma_decimal - (std_dev_decimal * Decimal(data.standard_deviation_multiplier))
        
        # Since the database expects Decimals, ensure that the final values are Decimal
        # Store the calculation result as strings to preserve precision
        db_manager.create_calculation_result(
            job_id=job.job_id,
            upper_band={"value": str(upper_band)},
            middle_band={"value": str(sma_decimal)},
            lower_band={"value": str(lower_band)}
        )
    else:
        # Handle the case where there's not enough data to calculate
        raise HTTPException(status_code=400, detail="Not enough data to calculate Bollinger Bands")

    db.refresh(job)
    return job

@app.get("/result/{job_id}", response_model=CalculationJobDetailOutput)
def retrieve_bollinger_result(job_id: str, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    job = db_manager.get_calculation_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Calculation job not found")
    return job

@app.post("/orders", response_model=FakeLimitOrderOutput)
def submit_fake_order(data: FakeLimitOrderCreate, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    order = db_manager.create_fake_limit_order(
        price=data.price, 
        quantity=data.quantity, 
        direction=data.direction
    )
    db.refresh(order)
    return order

@app.put("/orders/{order_id}", status_code=200)
def edit_fake_order(order_id: str, data: FakeLimitOrderCreate, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    if db_manager.update_fake_limit_order(order_id=order_id, **data.dict()):
        return {"message": "Order updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/orders/{order_id}", status_code=200)
def delete_fake_order(order_id: str, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    if db_manager.delete_fake_limit_order(order_id=order_id):
        return {"message": "Order deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.get("/orders", response_model=list[FakeLimitOrderOutput])
def list_all_fake_orders(db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    orders = db_manager.list_all_fake_limit_orders()
    return orders

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# <CreateMainFastApiFile/>
# <context:MainEndpoints/>
