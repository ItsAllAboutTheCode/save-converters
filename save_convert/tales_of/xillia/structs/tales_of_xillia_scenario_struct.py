"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_char, c_float, c_int32, c_uint8, c_uint16, c_uint32
from math import degrees, radians
from typing import Any, cast, override

from save_convert.structs.marshal_structure import (
    FromDictResult,
    MarshalStructure,
    ToDictResult,
    assert_field_offset,
    assert_struct_size,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_scenario_dict import ScenarioSaveDict, create_scenario_save_dict
from save_convert.tales_of.xillia.structs.tales_of_xillia_math_structs import UniqVector3f, Vector3f


class Scenario(MarshalStructure):
    class GlobalBuffer(MarshalStructure):
        class Global(MarshalStructure):
            class IDString(MarshalStructure):
                _fields_ = [
                    ("nID", c_int32),
                    ("szUniqName", c_char * 4),
                ]

            class DungeonTUN(MarshalStructure):
                _fields_ = [
                    ("nFlg", c_uint32),
                    ("nRockHP", c_uint32 * 32),
                    ("nOreItem", c_uint32 * 16),
                ]

            class DungeonARM(MarshalStructure):
                _fields_ = [
                    ("aBlock", UniqVector3f * 3),
                    ("nLiftFloor", c_uint32),
                ]

            class MapTerrainData(MarshalStructure):
                _fields_ = [
                    ("szTerrainName", c_char * 4),
                    ("szTerrainFile", c_char * 4),
                    ("x", c_float),
                    ("y", c_float),
                    ("z", c_float),
                    ("nDir", c_uint32),
                ]

            class DungeonFNL(MarshalStructure):
                _fields_ = [("nStepOnSwitchGNo", c_uint16), ("nStepOnSwitchBNo", c_uint16)]

            class DungeonCAS(MarshalStructure):
                _fields_ = [
                    ("nElvStartupFloor", c_uint16),
                    ("__align_to_4__", c_uint8 * 2),
                ]

            class DungeonELE(MarshalStructure):
                _fields_ = [
                    ("aBlock", UniqVector3f * 2),
                ]

            class DungeonHOM(DungeonELE):
                pass

            class DungeonFOR(MarshalStructure):
                class DisableCount(MarshalStructure):
                    _fields_ = [
                        ("nDisableCount", c_uint32),
                    ]

                _fields_ = [
                    ("aPoisonMushroom", DisableCount * 8),
                ]

            class DungeonURS(MarshalStructure):
                _fields_ = [
                    ("nStepOnSwitchGNo", c_uint16),
                    ("nStepOnSwitchBNo", c_uint16),
                    ("nGimmickFlg", c_uint32),
                ]

            class DungeonHOM_SCH(MarshalStructure):
                _fields_ = [
                    ("nShortChatOccurCount", c_uint32),
                    ("nShortChatFlg", c_uint32),
                ]

            class DungeonTUN_ORE(MarshalStructure):
                class TableIndexNum(MarshalStructure):
                    _fields_ = [("nTableIndexNo", c_uint16)]

                _fields_ = [
                    ("nSetNum", c_uint16),
                    ("aOreData", TableIndexNum * 10),
                ]

            _fields_ = [
                ("_adjust", c_uint32),  # offset abs=0x42B8
                ("dummy", c_uint32),  # offset abs=0x42BC
                ("__padding0__", c_uint8 * 52),
                ("aRTMapGadgetCtrl", IDString * 32),  # offset abs=0x42F4
                ("nDUN_UND_FLG", c_uint32),  # offset abs=0x43F4
                ("aDUN_TUN_001", DungeonTUN),  # offset abs=0x44BC
                ("aDUN_TUN_002", DungeonTUN),  # offset abs=0x44BC
                ("aDUN_ARM_010", DungeonARM),  # offset abs=0x4580
                ("aDUN_ARM_011", DungeonARM),
                ("aDUN_ARM_012", DungeonARM),
                ("aDUN_ARM_013", DungeonARM),
                ("aDUN_ARM_014", DungeonARM),
                ("aDUN_ARM_015", DungeonARM),
                ("aDUN_ARM_016", DungeonARM),
                ("aDUN_ARM_017", DungeonARM),
                ("aRTMapTerrainCtrl", MapTerrainData * 32),  # offset abs=0x4720
                ("aDUN_FNL", DungeonFNL),  # offset abs=0x4A20
                ("aDUN_CAS", DungeonCAS),  # offset abs=0x4A24
                ("aDUN_ELE_015", DungeonELE),  # offset abs=0x4A28
                ("aDUN_ELE_018", DungeonELE),
                ("aDUN_ELE_021", DungeonELE),
                ("nSUB_001_0_Wing", c_uint32),  # offset abs=0x4A88
                ("aDUN_HOM_013", DungeonHOM),  # offset abs=0x4A8C
                ("aDUN_HOM_023", DungeonHOM),
                ("aDUN_FOR_001", DungeonFOR),  # offset abs=0x4ACC
                ("aDUN_FOR_002", DungeonFOR),
                ("aDUN_FOR_003", DungeonFOR),
                ("nSUB_001_0_Wing_Total", c_uint32),  # offset abs=0x4B2C
                ("aDUN_URS", DungeonURS),  # offset abs=0x4B30
                ("aDUN_HOM_SCH", DungeonHOM_SCH),  # offset abs=0x4B38
                ("aDUN_TUN_001_ORE", DungeonTUN_ORE),  # offset abs=0x4B40
                ("aDUN_TUN_002_ORE", DungeonTUN_ORE),  # offset abs=0x4B56
                ("bDUN_CAS_000_MC_CTRL_SE", c_bool),  # offset abs=0x4B6C
                ("bDUN_CAS_009_MC_CTRL_SE", c_bool),  # offset abs=0x4B6D
                ("bDUN_CAS_010_MC_CTRL_SE", c_bool),  # offset abs=0x4B6E
                ("bDUN_CAS_011_MC_CTRL_SE", c_bool),  # offset abs=0x4B6F
                ("bTOW_GRG_ELV_CTRL_SE", c_bool),  # offset abs=0x4B70
                ("bDUN_ELE_ELV_CTRL_SE", c_bool),  # offset abs=0x4B71
                ("bIND_MAC_ELV_CTRL_SE", c_bool),  # offset abs=0x4B72
                ("__padding1__", c_uint8),  # offset abs=0x4B73
                ("aDUN_TUN_000", DungeonTUN),  # offset abs=0x4B74
                ("bBattleEventWaitBoot", c_bool),  # offset abs=0x4C38
                ("bDUN_HOM_005_MC_CTRL_SE", c_bool),  # offset abs=0x4C39
                ("bDUN_HOM_011_MC_CTRL_SE", c_bool),  # offset abs=0x4C3A
                ("bDUN_HOM_015_MC_CTRL_SE", c_bool),  # offset abs=0x4C3B
                ("bDUN_HOM_021_MC_CTRL_SE", c_bool),  # offset abs=0x4C3C
                ("__padding2__", c_uint8 * 3),  # offset abs=0x4C3D
                ("nDUN_TUN_DIG_ORE_NUM", c_uint32),  # offset abs=0x4C40
                ("bDUN_ARM_ELV_CTRL_SE", c_bool),  # offset abs=0x4C44
                ("__padding3__", c_uint8 * 3),  # offset abs=0x4C45
                ("nFNL_HELP_ORDER", c_uint32 * 4),  # offset abs=0x4C48
                ("nFNL_007_TRAP_SEED", c_uint32),  # offset abs=0x4C58
                ("nSNO_000_ROPEWAY_ARRIVAL_SE_FLAG", c_uint32),  #  offset abs=0x4C5C
                ("nSNO_002_ROPEWAY_ARRIVAL_SE_FLAG", c_uint32),  #  offset abs=0x4C60
            ]

        _fields_ = [("global", Global)]

        assert_field_offset(Global, "nSNO_002_ROPEWAY_ARRIVAL_SE_FLAG", 0x4C60 - 0x42B8)

    _fields_ = [
        ("map", c_char * 32),  # offset rel=0x0, abs=0x4270
        ("pos", Vector3f),  # offset rel=0x20, abs=0x4290
        ("dir", c_float),  # offset rel=0x2C, abs=0x429C
        ("start", Vector3f),  # offset rel=0x30, abs=0x42A0
        ("version", c_uint16),  # offset rel=0x3C, abs=0x42AC
        ("route", c_uint16),  # offset rel=0x3E, abs=0x42AE
        ("flag", c_uint32),  # offset rel=0x40, abs=0x42B0
        ("yaw", c_float),  # offset rel=0x44, abs=0x42B4
        ("globalbuffer", GlobalBuffer),  # offset rel=0x48, abs=0x42B8
        ("__align_to_16512__", c_uint8 * 13964),  # offset rel=0x9F4, abs=0x4C64
        ("bitflags", c_uint8 * 512),  # offset rel=0x4080, abs=0x82F0
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

        return ToDictResult(True, output_dict)

    @override
    @staticmethod
    def from_dict(
        input_dict: dict[str, Any], struct_type: type[MarshalStructure], skip_double_underscore_fields: bool = True
    ) -> FromDictResult[MarshalStructure]:
        """
        Convert Remaster save from Unity left-handed coordinate system
        to the PS3 raw data right-handed coordinate system
        """
        struct_result = MarshalStructure.from_dict(input_dict, struct_type, skip_double_underscore_fields)
        if not struct_result or not struct_result.value:
            return struct_result

        def enlarge_vector_100x(struct_inst: MarshalStructure, vector3_key: str):
            if vector3_inst := getattr(struct_inst, vector3_key):
                vector3_inst.x *= -100  # negative x
                vector3_inst.y *= 100  # positive y
                vector3_inst.z *= -100  # negative z

        def deg_to_rad(struct_inst: MarshalStructure, angle_key: str):
            setattr(struct_inst, angle_key, radians(getattr(struct_inst, angle_key, 0.0)))

        # convert the vector to have positive z / scale up by 100x
        enlarge_vector_100x(struct_result.value, "pos")
        enlarge_vector_100x(struct_result.value, "start")
        # convert degrees to radians
        deg_to_rad(struct_result.value, "dir")
        deg_to_rad(struct_result.value, "yaw")
        return struct_result


assert_field_offset(Scenario, "yaw", 0x44)
assert_field_offset(Scenario, "globalbuffer", 0x48)
assert_field_offset(Scenario, "__align_to_16512__", 0x9F4)
assert_field_offset(Scenario, "bitflags", 0x4080)

assert_struct_size(Scenario, 0x4280)
