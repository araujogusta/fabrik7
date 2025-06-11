from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict

FieldType = Literal['BOOL', 'BYTE', 'CHAR', 'WORD', 'DWORD', 'INT', 'DINT', 'REAL', 'LREAL']


class Field(BaseModel):
    name: str
    offset: int
    type: FieldType
    value: Optional[Any]

    model_config = ConfigDict(from_attributes=True)


class DB(BaseModel):
    number: int
    size: int
    fields: list[Field]

    model_config = ConfigDict(from_attributes=True)


class PLC(BaseModel):
    name: str
    host: Optional[str] = '127.0.0.1'
    port: Optional[int] = 102
    dbs: list[DB]

    model_config = ConfigDict(from_attributes=True)


class Config(BaseModel):
    plcs: list[PLC]
