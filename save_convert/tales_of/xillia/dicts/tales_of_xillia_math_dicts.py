"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class Color(TypedDict):
    r: float
    g: float
    b: float
    a: float


class Vector2(TypedDict):
    x: float
    y: float


class Vector3(TypedDict):
    x: float
    y: float
    z: float


class UniqVector3(Vector3):
    nUniqNo: int


class Matrix(TypedDict):
    e00: float
    e01: float
    e02: float
    e03: float
    e10: float
    e11: float
    e12: float
    e13: float
    e20: float
    e21: float
    e22: float
    e23: float
    e30: float
    e31: float
    e32: float
    e33: float
