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
from pydantic import BaseModel, condecimal, UUID4
from datetime import datetime
from enum import Enum
from typing import List, Optional

# Enums for the statuses similar to the ones in the database model
class CalculationJobStatus(str, Enum):
    pending = 'pending'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'

class FakeLimitOrderStatus(str, Enum):
    open = 'open'
    cancelled = 'cancelled'
    executed = 'executed'

class FakeLimitOrderDirection(str, Enum):
    buy = 'buy'
    sell = 'sell'

# Pydantic models for each database model
class CalculationJobCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    period: int
    standard_deviation_multiplier: float

class CalculationJobOutput(BaseModel):
    job_id: UUID4
    start_time: datetime
    end_time: datetime
    period: int
    standard_deviation_multiplier: float
    status: CalculationJobStatus
    created_at: datetime
    updated_at: datetime

class CalculationResultOutput(BaseModel):
    result_id: UUID4
    job_id: UUID4
    upper_band: dict
    middle_band: dict
    lower_band: dict
    calculated_at: datetime

class CalculationJobDetailOutput(CalculationJobOutput):
    results: List[CalculationResultOutput]

class FakeLimitOrderCreate(BaseModel):
    price: condecimal(decimal_places=2)
    quantity: condecimal(decimal_places=2)
    direction: FakeLimitOrderDirection

class FakeLimitOrderOutput(BaseModel):
    order_id: UUID4
    type: str
    price: condecimal(decimal_places=2)
    quantity: condecimal(decimal_places=2)
    direction: FakeLimitOrderDirection
    status: FakeLimitOrderStatus
    created_at: datetime
    updated_at: datetime

# Pydantic models for PriceData if it is ever needed for inputs or outputs
class PriceDataOutput(BaseModel):
    id: UUID4
    timestamp: datetime
    price: condecimal(decimal_places=2)
    volume: Optional[condecimal(decimal_places=2)]
# <CreatePydanticModels/>
# <context:PydanticModels/>