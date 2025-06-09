from typing import Literal

from pydantic import BaseModel, ConfigDict


class Field(BaseModel):
    name: str
    offset: int
    dtype: Literal['BOOL', 'BYTE', 'CHAR', 'WORD', 'DWORD', 'INT', 'DINT', 'REAL', 'LREAL', 'STRING']

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
