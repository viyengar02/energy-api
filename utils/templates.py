from typing import Optional
from pydantic import BaseModel

class BoardData(BaseModel):
    VA_MAG: float
    VB_MAG: float
    VC_MAG: float
    IA_MAG: float
    IB_MAG: float
    IC_MAG: float
    VA_ANG: float
    VB_ANG: float
    VC_ANG: float
    IA_ANG: float
    IB_ANG: float
    IC_ANG: float
    POW_FACTOR: float
    POW_APPARENT: float
    POW_ACTIVE: float
    POW_REACTIVE: float

class BoardLoginInformation(BaseModel):
    id: str
    board_type: str

class BoardPinConfiguration(BaseModel):
    PIN_1: Optional[str]
    PIN_2: Optional[str]
    PIN_3: Optional[str]
    PIN_4: Optional[str]
    PIN_5: Optional[str]

class UserInformation(BaseModel):
    username: str
    password: str
    email: str

class LoginUser(BaseModel):
    email: str
    password: str

class OptimizationThreshold(BaseModel):
    optimize: bool
    power_threshold: float