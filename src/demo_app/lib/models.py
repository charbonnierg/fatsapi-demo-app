"""This module defines data models used accross the application."""
from __future__ import annotations

import typing

from pydantic import BaseModel, Field


class EmployeeOptionalData(BaseModel):
    age: typing.Optional[int] = None
    favorite_animal: typing.Optional[str] = None
    hobby: typing.Optional[str] = None


class EmployeeFormCreate(EmployeeOptionalData):
    lastname: str
    firstname: str
    team: str


class EmployeeFormUpdate(EmployeeOptionalData):
    lastname: typing.Optional[str] = None
    firstname: typing.Optional[str] = None
    team: typing.Optional[str] = None


class EmployeeInDB(EmployeeFormCreate, allow_population_by_field_name=True):
    id: str = Field(..., alias="_id")


class EmployeeDump(BaseModel):
    __root__: typing.List[EmployeeInDB]
