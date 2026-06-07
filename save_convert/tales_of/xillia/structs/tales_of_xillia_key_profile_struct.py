"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField


class KEY_PROFILE_SAVE_DATAPLAYER(FillEndianSwapStructure):  #  type: ignore[metaclass]
    _size_ = 0x1000
    _offset_fields_ = [
        OffsetField(0x0, ("__unknown_button_action1__", c_uint32)),  # player 1 offset abs=0x444F0
        OffsetField(0x4, ("__unknown_button_code1__", c_uint32)),  # player 1 offset abs=0x444F4
        OffsetField(0x8, ("__unknown_button_action2__", c_uint32)),  # player 1 offset abs=0x444F8
        OffsetField(0xC, ("__unknown_button_code2__", c_uint32)),  # player 1 offset abs=0x444FC
        OffsetField(0x10, ("__unknown_button_action3__", c_uint32)),  # player 1 offset abs=0x44500
        OffsetField(0x14, ("__unknown_button_code3__", c_uint32)),  # player 1 offset abs=0x44504
        OffsetField(0x18, ("__normal_attack_button_action__", c_uint32)),  # player 1 offset abs=0x44508
        OffsetField(0x1C, ("__normal_attack_button_code__", c_uint32)),  # player 1 offset abs=0x4550C
        OffsetField(0x20, ("__arte_attack_button_action__", c_uint32)),  # player 1 offset abs=0x44510
        OffsetField(0x24, ("__arte_attack_button_code__", c_uint32)),  # player 1 offset abs=0x45514
        OffsetField(0x28, ("__guard_button_action__", c_uint32)),  # player 1 offset abs=0x44518
        OffsetField(0x2C, ("__guard_button_code__", c_uint32)),  # player 1 offset abs=0x4451C
        OffsetField(0x30, ("__menu_button_action__", c_uint32)),  # player 1 offset abs=0x44520
        OffsetField(0x34, ("__menu_button_code__", c_uint32)),  # player 1 offset abs=0x44524
        OffsetField(0x38, ("__function_shift_button_action__", c_uint32)),  # player 1 offset abs=0x44528
        OffsetField(0x3C, ("__function_shift_button_code__", c_uint32)),  # player 1 offset abs=0x4452C
        OffsetField(0x40, ("__unknown_button_action4__", c_uint32)),  # player 1 offset abs=0x44530
        OffsetField(0x44, ("__unknown_button_code4__", c_uint32)),  # player 1 offset abs=0x44534
        OffsetField(0x48, ("__free_run_button_action__", c_uint32)),  # player 1 offset abs=0x44538
        OffsetField(0x4C, ("__free_run_button_code__", c_uint32)),  # player 1 offset abs=0x4453C
        OffsetField(0x50, ("__change_target_button_action__", c_uint32)),  # player 1 offset abs=0x44540
        OffsetField(0x54, ("__change_target_button_code__", c_uint32)),  # player 1 offset abs=0x44544
        OffsetField(0x58, ("__linked_arte_button_action__", c_uint32)),  # player 1 offset abs=0x44548
        OffsetField(0x5C, ("__linked_arte_button_code__", c_uint32)),  # player 1 offset abs=0x4454C
        OffsetField(0x60, ("__unknown_button_action5__", c_uint32)),  # player 1 offset abs=0x44550
        OffsetField(0x64, ("__unknown_button_code5__", c_uint32)),  # player 1 offset abs=0x44554
        OffsetField(0x68, ("__unknown_button_action6__", c_uint32)),  # player 1 offset abs=0x44558
        OffsetField(0x6C, ("__unknown_button_code6__", c_uint32)),  # player 1 offset abs=0x4455C
    ]

    def __init__(self):
        """Initializes the KEY_PROFILE section with default values for PS3
        This required when converting a save back to PS3 format.
        This is sourced from a PS3 save with no modifications to the mapped buttons
        """
        super().__init__()
        self.__unknown_button_action1__ = 0x1C
        self.__unknown_button_code1__ = 0x2000000
        self.__unknown_button_action2__ = 0x1D
        self.__unknown_button_code2__ = 0x1000000
        self.__unknown_button_action3__ = 0x1E
        self.__unknown_button_code3__ = 0x10
        self.__normal_attack_button_action__ = 0x1F
        self.__normal_attack_button_code__ = 0x20
        self.__arte_attack_button_action__ = 0x20
        self.__arte_attack_button_code__ = 0x80
        self.__guard_button_action__ = 0x21
        self.__guard_button_code__ = 0x40
        self.__menu_button_action__ = 0x22
        self.__menu_button_code__ = 0x10
        self.__function_shift_button_action__ = 0x23
        self.__function_shift_button_code__ = 0x40000
        self.__unknown_button_action4__ = 0x24
        self.__unknown_button_code4__ = 0x80000
        self.__free_run_button_action__ = 0x25
        self.__free_run_button_code__ = 0x100000
        self.__change_target_button_action__ = 0x26
        self.__change_target_button_code__ = 0x200000
        self.__linked_arte_button_action__ = 0x27
        self.__linked_arte_button_code__ = 0x400000
        self.__unknown_button_action5__ = 0x28
        self.__unknown_button_code5__ = 0x800000
        self.__unknown_button_action6__ = 0x29
        self.__unknown_button_code6__ = 0x10000


assert_struct_no_padding(KEY_PROFILE_SAVE_DATAPLAYER)
