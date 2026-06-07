"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_float, c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_size
from save_convert.structs.marshal_structure import (
    MarshalStructure,
)


class Matrix(MarshalStructure):
    _fields_ = [
        ("e00", c_float),
        ("e01", c_float),
        ("e02", c_float),
        ("e03", c_float),
        ("e10", c_float),
        ("e11", c_float),
        ("e12", c_float),
        ("e13", c_float),
        ("e20", c_float),
        ("e21", c_float),
        ("e22", c_float),
        ("e23", c_float),
        ("e30", c_float),
        ("e31", c_float),
        ("e32", c_float),
        ("e33", c_float),
    ]


class Color(MarshalStructure):
    _fields_ = [
        ("r", c_float),
        ("g", c_float),
        ("b", c_float),
        ("a", c_float),
    ]


class Vector2i(MarshalStructure):
    _fields_ = [
        ("x", c_uint32),
        ("y", c_uint32),
    ]


class Vector3f(MarshalStructure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
    ]


class UniqVector3f(MarshalStructure):
    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float), ("nUniqNo", c_uint32)]


assert_struct_size(Matrix, 0x40)
assert_struct_size(Color, 0x10)
assert_struct_size(Vector2i, 0x8)
assert_struct_size(Vector3f, 0xC)
assert_struct_size(UniqVector3f, 0x10)
