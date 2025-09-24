from typing import TypedDict, Optional


class EngineStatus(TypedDict):
    address: str
    connected: bool
    pool_minsize: Optional[int]
    pool_maxsize: Optional[int]
    pool_size: Optional[int]
    pool_free: Optional[int]
    pool_used: Optional[int]