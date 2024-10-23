from typing import Optional
from typing import List
from pydantic import BaseModel, validator
from fastapi import HTTPException

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


class BoardDummyInfo(BaseModel):
    board_id: str
    ade_id: int

class BoardDataDummy(BaseModel):
    id: str
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
    board_info: BoardDummyInfo

class PostBoardData(BaseModel):
    data: List[BoardDataDummy]

class BoardPinConfiguration(BaseModel):
    PIN_1: Optional[int]
    PIN_2: Optional[int]
    PIN_3: Optional[int]
    PIN_4: Optional[int]
    PIN_5: Optional[int]

class UserInformation(BaseModel):
    username: str
    password: str
    email: str
    auth_lvl: str

class LoginUser(BaseModel):
    email: str
    password: str

class BoardAuthLvl(BaseModel):
    auth_lvl: str

class OptimizationThreshold(BaseModel):    
    optimize: int
    value: float

    @validator('optimize', pre=True)
    def validate_optimize(cls, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise HTTPException(status_code=400, detail="Bad Request - optimize can be 0, 1 or 2")
        return value