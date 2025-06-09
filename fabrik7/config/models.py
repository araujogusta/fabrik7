from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict

_DType = Literal['BOOL', 'BYTE', 'CHAR', 'WORD', 'DWORD', 'INT', 'DINT', 'REAL', 'LREAL']


class Field(BaseModel):
    name: str
    offset: int
    dtype: _DType
    value: Optional[Any]

    model_config = ConfigDict(from_attributes=True)


class DB(BaseModel):
    number: int
    size: int
    fields: list[Field]

    model_config = ConfigDict(from_attributes=True)


class PLC(BaseModel):
    name: str
    port: int
    dbs: list[DB]

    model_config = ConfigDict(from_attributes=True)


class Config(BaseModel):
    plcs: list[PLC]
