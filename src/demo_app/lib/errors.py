"""This module provides error classes to use within library code."""
from __future__ import annotations


class EmployeeNotFoundError(KeyError):
    """A class raised when query did not match any known employee"""

    pass
