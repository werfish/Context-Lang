# <file:ENPOINTS>Endpoints.txt<file:ENDPOINTS/>
# <file:MANIFEST>MANIFEST.txt<file:MANIFEST/>
# <import:DB_MODELS_PY>db_models.py<import:DB_MODELS_PY/>

# <prompt:CreatePydanticModels>
# Please implement Pydantic models for input and output of the api.
# For context you will get the monifest of the project describing high level requirements.
# You will also get the endpoints file to understand the design of the api endpoints.
# And also the db models file to understand the structure of the database.
# {MANIFEST}
# {ENDPOINTS}
# {DB_MODELS_PY}
# <prompt:CreatePydanticModels/>

# <context:PydanticModels>
# <CreatePydanticModels>
# pydantic_models.py
from pydantic import BaseModel, UUID4, condecimal
from datetime import datetime
from typing import Optional, Dict
from enum import Enum

# Enums used for Pydantic validation
class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class OrderStatus(str, Enum):
    open = "open"
    cancelled = "cancelled"
    executed = "executed"

class OrderDirection(str, Enum):
    buy = "buy"
    sell = "sell"

# Pydantic models for CalculationJob
class CalculationJobInput(BaseModel):
    start_time: datetime
    end_time: datetime
    period: int
    standard_deviation_multiplier: float

class CalculationJobOutput(BaseModel):
    job_id: UUID4
    start_time: datetime
    end_time: datetime
    status: JobStatus
    period: int
    standard_deviation_multiplier: float
    created_at: datetime
    updated_at: datetime

# Pydantic models for CalculationResult
class CalculationResultOutput(BaseModel):
    result_id: UUID4
    job_id: UUID4
    upper_band: Dict[str, float]
    middle_band: Dict[str, float]
    lower_band: Dict[str, float]
    calculated_at: datetime

# Pydantic models for FakeLimitOrder
class FakeLimitOrderInput(BaseModel):
    price: condecimal(decimal_places=2)  # Precision based on USD amount in crypto
    quantity: condecimal(decimal_places=8)  # Precision based on crypto amount
    direction: OrderDirection

class FakeLimitOrderOutput(BaseModel):
    order_id: UUID4
    type: str
    price: condecimal(decimal_places=2)
    quantity: condecimal(decimal_places=8)
    direction: OrderDirection
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
# <CreatePydanticModels/>
# <context:PydanticModels/>