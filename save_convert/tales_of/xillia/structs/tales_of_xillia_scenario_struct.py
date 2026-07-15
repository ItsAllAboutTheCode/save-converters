"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_char, c_float, c_int32, c_uint8, c_uint16, c_uint32
from math import degrees, radians
from typing import Any, cast, override

from save_convert.structs.marshal_dict_base import FromDictResult, MarshalStructDictBase, ToDictResult
from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField
from save_convert.tales_of.xillia.dicts.tales_of_xillia_scenario_dict import ScenarioSaveDict, create_scenario_save_dict
from save_convert.tales_of.xillia.structs.tales_of_xillia_math_structs import UniqVector3f, Vector3f


class Scenario(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class GlobalBuffer(FillEndianSwapStructure):  #  type: ignore[metaclass]
        class Global(FillEndianSwapStructure):  #  type: ignore[metaclass]
            class IDString(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x8
                _offset_fields_ = [
                    OffsetField(0x0, ("nID", c_int32)),
                    OffsetField(0x4, ("szUniqName", c_char * 4)),
                ]

            class DungeonTUN(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0xC4
                _offset_fields_ = [
                    OffsetField(0x0, ("nFlg", c_uint32)),
                    OffsetField(0x4, ("nRockHP", c_uint32 * 32)),
                    OffsetField(0x84, ("nOreItem", c_uint32 * 16)),
                ]

            class DungeonARM(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x34
                _offset_fields_ = [
                    OffsetField(0x0, ("aBlock", UniqVector3f * 3)),
                    OffsetField(0x30, ("nLiftFloor", c_uint32)),
                ]

            class MapTerrainData(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x18
                _offset_fields_ = [
                    OffsetField(0x0, ("szTerrainName", c_uint8 * 4)),
                    OffsetField(0x4, ("szTerrainFile", c_uint8 * 4)),
                    OffsetField(0x8, ("x", c_float)),
                    OffsetField(0xC, ("y", c_float)),
                    OffsetField(0x10, ("z", c_float)),
                    OffsetField(0x14, ("nDir", c_uint32)),
                ]

            class DungeonFNL(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x4
                _offset_fields_ = [
                    OffsetField(0x0, ("nStepOnSwitchGNo", c_uint16)),
                    OffsetField(0x2, ("nStepOnSwitchBNo", c_uint16)),
                ]

            class DungeonCAS(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x4
                _offset_fields_ = [
                    OffsetField(0x0, ("nElvStartupFloor", c_uint16)),
                ]

            class DungeonELE(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x20
                _offset_fields_ = [
                    OffsetField(0x0, ("aBlock", UniqVector3f * 2)),
                ]

            DungeonHOM = DungeonELE

            class DungeonFOR(FillEndianSwapStructure):  #  type: ignore[metaclass]
                class DisableCount(FillEndianSwapStructure):  #  type: ignore[metaclass]
                    _size_ = 0x4
                    _offset_fields_ = [
                        OffsetField(0x0, ("nDisableCount", c_uint32)),
                    ]

                _size_ = 0x20
                _offset_fields_ = [
                    OffsetField(0x0, ("aPoisonMushroom", DisableCount * 8)),  #  type: ignore[arg-type,operator]
                ]

            class DungeonURS(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x8
                _offset_fields_ = [
                    OffsetField(0x0, ("nStepOnSwitchGNo", c_uint16)),
                    OffsetField(0x2, ("nStepOnSwitchBNo", c_uint16)),
                    OffsetField(0x4, ("nGimmickFlg", c_uint32)),
                ]

            class DungeonHOM_SCH(FillEndianSwapStructure):  #  type: ignore[metaclass]
                _size_ = 0x8
                _offset_fields_ = [
                    OffsetField(0x0, ("nShortChatOccurCount", c_uint32)),
                    OffsetField(0x4, ("nShortChatFlg", c_uint32)),
                ]

            class DungeonTUN_ORE(FillEndianSwapStructure):  #  type: ignore[metaclass]
                class TableIndexNum(FillEndianSwapStructure):  #  type: ignore[metaclass]
                    _size_ = 0x2
                    _offset_fields_ = [OffsetField(0x0, ("nTableIndexNo", c_uint16))]

                _size_ = 0x16
                _offset_fields_ = [
                    OffsetField(0x0, ("nSetNum", c_uint16)),
                    OffsetField(0x2, ("aOreData", TableIndexNum * 10)),  #  type: ignore[arg-type,operator]
                ]

            _size_ = 0x9AC
            _offset_fields_ = [
                OffsetField(0x0, ("_adjust", c_uint32)),  # offset abs=0x42B8
                OffsetField(0x4, ("dummy", c_uint32)),  # offset abs=0x42BC
                OffsetField(
                    0x3C,
                    ("aRTMapGadgetCtrl", IDString * 32),  #  type: ignore[arg-type,operator]
                ),  # offset abs=0x42F4
                OffsetField(0x13C, ("nDUN_UND_FLG", c_uint32)),  # offset abs=0x43F4
                OffsetField(0x140, ("aDUN_TUN_001", DungeonTUN)),  # offset abs=0x43F8
                OffsetField(0x204, ("aDUN_TUN_002", DungeonTUN)),  # offset abs=0x44BC
                OffsetField(0x2C8, ("aDUN_ARM_010", DungeonARM)),  # offset abs=0x4580
                OffsetField(0x2FC, ("aDUN_ARM_011", DungeonARM)),  # offset abs=0x45B4
                OffsetField(0x330, ("aDUN_ARM_012", DungeonARM)),  # offset abs=0x45E8
                OffsetField(0x364, ("aDUN_ARM_013", DungeonARM)),  # offset abs=0x461C
                OffsetField(0x398, ("aDUN_ARM_014", DungeonARM)),  # offset abs=0x4650
                OffsetField(0x3CC, ("aDUN_ARM_015", DungeonARM)),  # offset abs=0x4684
                OffsetField(0x400, ("aDUN_ARM_016", DungeonARM)),  # offset abs=0x46B8
                OffsetField(0x434, ("aDUN_ARM_017", DungeonARM)),  # offset abs=0x46EC
                OffsetField(0x468, ("aRTMapTerrainCtrl", MapTerrainData * 32)),  #  type: ignore[arg-type,operator] # offset abs=0x4720
                OffsetField(0x768, ("aDUN_FNL", DungeonFNL)),  # offset abs=0x4A20
                OffsetField(0x76C, ("aDUN_CAS", DungeonCAS)),  # offset abs=0x4A24
                OffsetField(0x770, ("aDUN_ELE_015", DungeonELE)),  # offset abs=0x4A28
                OffsetField(0x790, ("aDUN_ELE_018", DungeonELE)),  # offset abs=0x4A48
                OffsetField(0x7B0, ("aDUN_ELE_021", DungeonELE)),  # offset abs=0x4A68
                OffsetField(0x7D0, ("nSUB_001_0_Wing", c_uint32)),  # offset abs=0x4A88
                OffsetField(0x7D4, ("aDUN_HOM_013", DungeonHOM)),  # offset abs=0x4A8C
                OffsetField(0x7F4, ("aDUN_HOM_023", DungeonHOM)),  # offset abs=0x4AAC
                OffsetField(0x814, ("aDUN_FOR_001", DungeonFOR)),  # offset abs=0x4ACC
                OffsetField(0x834, ("aDUN_FOR_002", DungeonFOR)),  # offset abs=0x4AEC
                OffsetField(0x854, ("aDUN_FOR_003", DungeonFOR)),  # offset abs=0x4A0C
                OffsetField(0x874, ("nSUB_001_0_Wing_Total", c_uint32)),  # offset abs=0x4B2C
                OffsetField(0x878, ("aDUN_URS", DungeonURS)),  # offset abs=0x4B30
                OffsetField(0x880, ("aDUN_HOM_SCH", DungeonHOM_SCH)),  # offset abs=0x4B38
                OffsetField(0x888, ("aDUN_TUN_001_ORE", DungeonTUN_ORE)),  # offset abs=0x4B40
                OffsetField(0x89E, ("aDUN_TUN_002_ORE", DungeonTUN_ORE)),  # offset abs=0x4B56
                OffsetField(0x8B4, ("bDUN_CAS_000_MC_CTRL_SE", c_bool)),  # offset abs=0x4B6C
                OffsetField(0x8B5, ("bDUN_CAS_009_MC_CTRL_SE", c_bool)),  # offset abs=0x4B6D
                OffsetField(0x8B6, ("bDUN_CAS_010_MC_CTRL_SE", c_bool)),  # offset abs=0x4B6E
                OffsetField(0x8B7, ("bDUN_CAS_011_MC_CTRL_SE", c_bool)),  # offset abs=0x4B6F
                OffsetField(0x8B8, ("bTOW_GRG_ELV_CTRL_SE", c_bool)),  # offset abs=0x4B70
                OffsetField(0x8B9, ("bDUN_ELE_ELV_CTRL_SE", c_bool)),  # offset abs=0x4B71
                OffsetField(0x8BA, ("bIND_MAC_ELV_CTRL_SE", c_bool)),  # offset abs=0x4B72
                OffsetField(0x8BC, ("aDUN_TUN_000", DungeonTUN)),  # offset abs=0x4B74
                OffsetField(0x980, ("bBattleEventWaitBoot", c_bool)),  # offset abs=0x4C38
                OffsetField(0x981, ("bDUN_HOM_005_MC_CTRL_SE", c_bool)),  # offset abs=0x4C39
                OffsetField(0x982, ("bDUN_HOM_011_MC_CTRL_SE", c_bool)),  # offset abs=0x4C3A
                OffsetField(0x983, ("bDUN_HOM_015_MC_CTRL_SE", c_bool)),  # offset abs=0x4C3B
                OffsetField(0x984, ("bDUN_HOM_021_MC_CTRL_SE", c_bool)),  # offset abs=0x4C3C
                OffsetField(0x988, ("nDUN_TUN_DIG_ORE_NUM", c_uint32)),  # offset abs=0x4C40
                OffsetField(0x98C, ("bDUN_ARM_ELV_CTRL_SE", c_bool)),  # offset abs=0x4C44
                OffsetField(0x990, ("nFNL_HELP_ORDER", c_uint32 * 4)),  # offset abs=0x4C48
                OffsetField(0x9A0, ("nFNL_007_TRAP_SEED", c_uint32)),  # offset abs=0x4C58
                OffsetField(0x9A4, ("nSNO_000_ROPEWAY_ARRIVAL_SE_FLAG", c_uint32)),  #  offset abs=0x4C5C
                OffsetField(0x9A8, ("nSNO_002_ROPEWAY_ARRIVAL_SE_FLAG", c_uint32)),  #  offset abs=0x4C60
            ]

        _size_ = 0x9AC
        _offset_fields_ = [OffsetField(0x0, ("global", Global))]

    _size_ = 0x4280
    _offset_fields_ = [
        OffsetField(0x0, ("map", c_char * 32)),  # offset rel=0x0, abs=0x4270
        OffsetField(0x20, ("pos", Vector3f)),  # offset rel=0x20, abs=0x4290
        OffsetField(0x2C, ("dir", c_float)),  # offset rel=0x2C, abs=0x429C
        OffsetField(0x30, ("start", Vector3f)),  # offset rel=0x30, abs=0x42A0
        OffsetField(0x3C, ("version", c_uint16)),  # offset rel=0x3C, abs=0x42AC
        OffsetField(0x3E, ("route", c_uint16)),  # offset rel=0x3E, abs=0x42AE
        OffsetField(0x40, ("flag", c_uint32)),  # offset rel=0x40, abs=0x42B0
        OffsetField(0x44, ("yaw", c_float)),  # offset rel=0x44, abs=0x42B4
        OffsetField(0x48, ("globalbuffer", GlobalBuffer)),  # offset rel=0x48, abs=0x42B8
        OffsetField(0x4080, ("bitflags", c_uint8 * 512)),  # offset rel=0x4080, abs=0x82F0
    ]

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Transform the dictionary containing a loaded PS3 save into one suitable for the remastered game save

        Modifications:
        It appears that vector coordinates on PS3 is using a right-handed system with Y vs the
        Remastered platforms using the Unity left-handed system with Y up
        Also the vector appears to be scaled up by 100x on PS3.
        The rotation float on PS3 is stored in radians, while the PC version is stored in degrees.

        Convert Terrain 4-byte string buffer into an empty string

        TODO: Also the bitflags array needs modification in some way
        """

        # Initialize a default scenario save data dict with all the required
        # fields and then merge the marshaled results into it
        output_dict: ScenarioSaveDict = create_scenario_save_dict()
        dict_result = super().to_dict(skip_double_underscore_fields)

        if not dict_result or not dict_result.value:
            return dict_result

        output_dict |= cast(ScenarioSaveDict, cast(object, dict_result.value))

        def shrink_vector_100x(dict_section: ScenarioSaveDict, vector3_key: str):
            if isinstance(pos_value := dict_section.get(vector3_key), dict):
                if pos_x := pos_value.get("x"):
                    pos_value["x"] = pos_x / -100  # negative x
                if pos_y := pos_value.get("y"):
                    pos_value["y"] = pos_y / 100  # positive y
                if pos_z := pos_value.get("z"):
                    pos_value["z"] = pos_z / -100  # negative z

        def rad_to_deg(dict_section: ScenarioSaveDict, angle_key: str):
            if isinstance(angle_value := dict_section.get(angle_key), float):
                dict_section[angle_key] = degrees(angle_value)  # type: ignore[literal-required]

        # convert the vector to have negative z / scale down by 100x
        shrink_vector_100x(output_dict, "pos")
        shrink_vector_100x(output_dict, "start")
        # convert radians to degrees
        rad_to_deg(output_dict, "dir")
        rad_to_deg(output_dict, "yaw")

        output_dict["globalbuffer"]["global"]["aRTMapTerrainCtrl"]
        try:
            terrain_map_ctrl_list = output_dict["globalbuffer"]["global"]["aRTMapTerrainCtrl"]
        except KeyError:
            return ToDictResult(False)

        for terrain_data in terrain_map_ctrl_list:
            terrain_data["szTerrainName"] = ""
            terrain_data["szTerrainFile"] = ""

        return ToDictResult(True, output_dict)

    @override
    @staticmethod
    def from_dict(
        input_dict: dict[str, Any], struct_type: type[MarshalStructDictBase], skip_double_underscore_fields: bool = True
    ) -> FromDictResult[MarshalStructDictBase]:
        """
        Convert Remaster save from Unity left-handed coordinate system
        to the PS3 raw data right-handed coordinate system
        """
        struct_result = MarshalStructDictBase.from_dict(input_dict, struct_type, skip_double_underscore_fields)
        if not struct_result or not struct_result.value:
            return struct_result

        def enlarge_vector_100x(struct_inst: MarshalStructDictBase, vector3_key: str):
            if vector3_inst := getattr(struct_inst, vector3_key):
                vector3_inst.x *= -100  # negative x
                vector3_inst.y *= 100  # positive y
                vector3_inst.z *= -100  # negative z

        def deg_to_rad(struct_inst: MarshalStructDictBase, angle_key: str):
            setattr(struct_inst, angle_key, radians(getattr(struct_inst, angle_key, 0.0)))

        # convert the vector to have positive z / scale up by 100x
        enlarge_vector_100x(struct_result.value, "pos")
        enlarge_vector_100x(struct_result.value, "start")
        # convert degrees to radians
        deg_to_rad(struct_result.value, "dir")
        deg_to_rad(struct_result.value, "yaw")
        return struct_result


assert_struct_no_padding(Scenario)
