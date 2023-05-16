from typing import Optional
from typing import List
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

class LoginUser(BaseModel):
    email: str
    password: str

class OptimizationThreshold(BaseModel):
    optimize: bool
    power_threshold: float