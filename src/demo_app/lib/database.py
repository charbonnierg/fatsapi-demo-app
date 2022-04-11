"""This module provides a class to facilitates data management and interaction with the demo database."""
from __future__ import annotations

import pathlib
import typing
import uuid

from .errors import EmployeeNotFoundError
from .models import EmployeeDump, EmployeeFormCreate, EmployeeFormUpdate, EmployeeInDB


class EmployeeDatabase:
    """A class used to perform mutations on employee databases easily"""

    def __init__(self, path: typing.Union[str, pathlib.Path]) -> None:
        self.path = pathlib.Path(path).resolve(True)
        self.employees = {
            employee.id: employee
            for employee in EmployeeDump.parse_file(self.path).__root__
        }

    def values(self) -> typing.List[EmployeeInDB]:
        """List holding all employees in database"""
        return list(self.employees.values())

    def json(self, **kwargs: typing.Any) -> str:
        """JSON representation of database state"""
        kwargs["exclude_unset"] = True
        return EmployeeDump.parse_obj(self.values()).json(**kwargs)

    def refresh(self) -> None:
        """Refresh database"""
        self.employees = {
            employee.id: employee
            for employee in EmployeeDump.parse_file(self.path).__root__
        }

    def save(self, **kwargs: typing.Any) -> None:
        """Save database state to file"""
        self.path.write_text(self.json(**kwargs))

    def filter(self, **kwargs: typing.Any) -> typing.Iterator[EmployeeInDB]:
        """Yield employees matching filters. By default all employees are yielded"""
        for employee in self.employees.values():
            employee_dict = employee.dict(by_alias=False)
            for field, expected_value in kwargs.items():
                value_in_db = employee_dict.get(field, ...)
                if value_in_db is ...:
                    break
                try:
                    if value_in_db != expected_value:
                        break
                except AttributeError:
                    break
            else:
                yield employee

    def find(self, **kwargs: typing.Any) -> typing.List[EmployeeInDB]:
        """Find a many employees, optionally using filters"""
        return list(self.filter(**kwargs))

    def find_one(self, **kwargs: typing.Any) -> EmployeeInDB:
        """Find a single employee, optionally using filter

        Raises:
            EmployeeNotFoundError: When no employee is found
        """
        # Return first employe found
        for employee in self.filter(**kwargs):
            return employee
        raise EmployeeNotFoundError(f"No employee found using filters: {kwargs}")

    def create_one(
        self, employee: EmployeeFormCreate, save: bool = True
    ) -> EmployeeInDB:
        """Create a new employee

        Raises:
            ValidationError: When employee data is not valid
        """
        _id = str(uuid.uuid4())
        self.employees[_id] = EmployeeInDB.parse_obj(
            {"_id": _id, **employee.dict(exclude_unset=True)}
        )
        if save:
            self.save()
        return self.employees[_id]

    def update_one(
        self,
        filters: typing.Dict[str, typing.Any],
        field_updates: EmployeeFormUpdate,
        create: bool = False,
        save: bool = True,
    ) -> EmployeeInDB:
        """Update an existing employee matching filter

        Raises:
            EmployeeNotFoundError: When filters do not match any employee
        """
        try:
            employee = self.find_one(**filters)
        except EmployeeNotFoundError:
            if create:
                new_fields = EmployeeFormCreate.parse_obj(field_updates)
                new_employee = self.create_one(new_fields)
                if save:
                    self.save()
                return new_employee
            else:
                raise
        self.employees[employee.id] = EmployeeInDB.parse_obj(
            employee.copy(update=field_updates.dict(exclude_unset=True, by_alias=True))
        )
        if save:
            self.save()
        return self.employees[employee.id]

    def delete_one(
        self, filters: typing.Dict[str, typing.Any], save: bool = True
    ) -> None:
        """Delete an existing employee matching filter

        Raises:
            EmployeeNotFoundError: When filters do not match any employee
        """
        employee = self.find_one(**filters)
        if employee:
            self.employees.pop(employee.id)
            if save:
                self.save()
