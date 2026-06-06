"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict

from save_convert.tales_of.xillia.dicts.tales_of_xillia_math_dicts import UniqVector3, Vector3


class IDString(TypedDict):
    nID: int
    szUniqName: str


class DungeonTUN(TypedDict):
    nFlg: int
    nRockHP: list[int]
    nOreItem: list[int]


class DungeonARM(TypedDict):
    aBlock: list[UniqVector3]
    nLiftFloor: int


class MapTerrainData(TypedDict):
    szTerrainName: str
    szTerrainFile: str
    x: float
    y: float
    z: float
    nDir: int


class DungeonFNL(TypedDict):
    nStepOnSwitchGNo: int
    nStepOnSwitchBNo: int


class DungeonCAS(TypedDict):
    nElvStartupFloor: int


class DungeonELE(TypedDict):
    aBlock: list[UniqVector3]


DungeonHOM = DungeonELE


class DisableCount(TypedDict):
    nDisableCount: int


class DungeonFOR(TypedDict):
    aPoisonMushroom: list[DisableCount]


class DungeonURS(TypedDict):
    nStepOnSwitchGNo: int
    nStepOnSwitchBNo: int
    nGimmickFlg: int


class DungeonHOM_SCH(TypedDict):
    nShortChatOccurCount: int
    nShortChatFlg: int


class TableIndexNum(TypedDict):
    nTableIndexNo: int


class DungeonTUN_ORE(TypedDict):
    nSetNum: int
    aOreData: list[TableIndexNum]


class Global(TypedDict):
    _adjust: int
    dummy: int
    aRTMapGadgetCtrl: list[IDString]
    nDUN_UND_FLG: int
    aDUN_TUN_001: DungeonTUN
    aDUN_TUN_002: DungeonTUN
    aDUN_ARM_010: DungeonARM
    aDUN_ARM_011: DungeonARM
    aDUN_ARM_012: DungeonARM
    aDUN_ARM_013: DungeonARM
    aDUN_ARM_014: DungeonARM
    aDUN_ARM_015: DungeonARM
    aDUN_ARM_016: DungeonARM
    aDUN_ARM_017: DungeonARM
    aRTMapTerrainCtrl: list[MapTerrainData]
    aDUN_FNL: DungeonFNL
    aDUN_CAS: DungeonCAS
    aDUN_ELE_015: DungeonELE
    aDUN_ELE_018: DungeonELE
    aDUN_ELE_021: DungeonELE
    nSUB_001_0_Wing: int
    aDUN_HOM_013: DungeonHOM
    aDUN_HOM_023: DungeonHOM
    aDUN_FOR_001: DungeonFOR
    aDUN_FOR_002: DungeonFOR
    aDUN_FOR_003: DungeonFOR
    nSUB_001_0_Wing_Total: int
    aDUN_URS: DungeonURS
    aDUN_HOM_SCH: DungeonHOM_SCH
    aDUN_TUN_001_ORE: DungeonTUN_ORE
    aDUN_TUN_002_ORE: DungeonTUN_ORE
    bDUN_CAS_000_MC_CTRL_SE: bool
    bDUN_CAS_009_MC_CTRL_SE: bool
    bDUN_CAS_010_MC_CTRL_SE: bool
    bDUN_CAS_011_MC_CTRL_SE: bool
    bTOW_GRG_ELV_CTRL_SE: bool
    bDUN_ELE_ELV_CTRL_SE: bool
    bIND_MAC_ELV_CTRL_SE: bool
    aDUN_TUN_000: DungeonTUN
    bBattleEventWaitBoot: bool
    bDUN_HOM_005_MC_CTRL_SE: bool
    bDUN_HOM_011_MC_CTRL_SE: bool
    bDUN_HOM_015_MC_CTRL_SE: bool
    bDUN_HOM_021_MC_CTRL_SE: bool
    nDUN_TUN_DIG_ORE_NUM: int
    bDUN_ARM_ELV_CTRL_SE: bool
    nFNL_HELP_ORDER: list[int]
    nFNL_007_TRAP_SEED: int
    nSNO_000_ROPEWAY_ARRIVAL_SE_FLAG: int
    nSNO_002_ROPEWAY_ARRIVAL_SE_FLAG: int


# The `global` term is reserved by python, so use the functional syntax
# to declare a type dict in this case
# https://typing.python.org/en/latest/spec/typeddict.html#typeddict
GlobalBuffer = TypedDict("GlobalBuffer", {"global": Global})


class ScenarioSaveDict(TypedDict):
    map: str
    pos: Vector3
    dir: float
    start: Vector3
    version: int
    route: int
    flag: int
    yaw: float
    globalbuffer: GlobalBuffer
    bitflags: list[int]


def create_scenario_save_dict() -> ScenarioSaveDict:
    return {
        "map": "DUN_INS_000",
        "pos": {"x": 0.0, "y": 0.0, "z": 8.0},
        "dir": -180.0,
        "start": {"x": 0.0, "y": 0.0, "z": 8.0},
        "version": 1,
        "route": 2,
        "flag": 20040,
        "yaw": 180.0,
        "globalbuffer": {
            "global": {
                "_adjust": 2376,
                "dummy": 0,
                "aRTMapGadgetCtrl": [IDString(nID=0, szUniqName="")] * 32,
                "nDUN_UND_FLG": 0,
                "aDUN_TUN_001": {"nFlg": 0, "nRockHP": [0] * 32, "nOreItem": [0] * 16},
                "aDUN_TUN_002": {"nFlg": 0, "nRockHP": [0] * 32, "nOreItem": [0] * 16},
                "aDUN_ARM_010": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aDUN_ARM_011": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aDUN_ARM_012": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aDUN_ARM_013": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aDUN_ARM_014": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aDUN_ARM_015": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aDUN_ARM_016": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aDUN_ARM_017": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 3, "nLiftFloor": 0},
                "aRTMapTerrainCtrl": [MapTerrainData(szTerrainName="", szTerrainFile="", x=0.0, y=0.0, z=0.0, nDir=0)]
                * 32,
                "aDUN_FNL": {"nStepOnSwitchGNo": 0, "nStepOnSwitchBNo": 0},
                "aDUN_CAS": {"nElvStartupFloor": 0},
                "aDUN_ELE_015": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 2},
                "aDUN_ELE_018": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 2},
                "aDUN_ELE_021": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 2},
                "nSUB_001_0_Wing": 0,
                "aDUN_HOM_013": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 2},
                "aDUN_HOM_023": {"aBlock": [UniqVector3(x=0.0, y=0.0, z=0.0, nUniqNo=0)] * 2},
                "aDUN_FOR_001": {
                    "aPoisonMushroom": [DisableCount(nDisableCount=0)] * 8,
                },
                "aDUN_FOR_002": {
                    "aPoisonMushroom": [DisableCount(nDisableCount=0)] * 8,
                },
                "aDUN_FOR_003": {
                    "aPoisonMushroom": [DisableCount(nDisableCount=0)] * 8,
                },
                "nSUB_001_0_Wing_Total": 0,
                "aDUN_URS": {"nStepOnSwitchGNo": 0, "nStepOnSwitchBNo": 0, "nGimmickFlg": 0},
                "aDUN_HOM_SCH": {"nShortChatOccurCount": 0, "nShortChatFlg": 0},
                "aDUN_TUN_001_ORE": {
                    "nSetNum": 0,
                    "aOreData": [TableIndexNum(nTableIndexNo=0)] * 10,
                },
                "aDUN_TUN_002_ORE": {
                    "nSetNum": 0,
                    "aOreData": [TableIndexNum(nTableIndexNo=0)] * 10,
                },
                "bDUN_CAS_000_MC_CTRL_SE": False,
                "bDUN_CAS_009_MC_CTRL_SE": False,
                "bDUN_CAS_010_MC_CTRL_SE": False,
                "bDUN_CAS_011_MC_CTRL_SE": False,
                "bTOW_GRG_ELV_CTRL_SE": False,
                "bDUN_ELE_ELV_CTRL_SE": False,
                "bIND_MAC_ELV_CTRL_SE": False,
                "aDUN_TUN_000": {
                    "nFlg": 0,
                    "nRockHP": [0] * 32,
                    "nOreItem": [0] * 16,
                },
                "bBattleEventWaitBoot": False,
                "bDUN_HOM_005_MC_CTRL_SE": False,
                "bDUN_HOM_011_MC_CTRL_SE": False,
                "bDUN_HOM_015_MC_CTRL_SE": False,
                "bDUN_HOM_021_MC_CTRL_SE": False,
                "nDUN_TUN_DIG_ORE_NUM": 0,
                "bDUN_ARM_ELV_CTRL_SE": False,
                "nFNL_HELP_ORDER": [0] * 4,
                "nFNL_007_TRAP_SEED": 0,
                "nSNO_000_ROPEWAY_ARRIVAL_SE_FLAG": 0,
                "nSNO_002_ROPEWAY_ARRIVAL_SE_FLAG": 0,
            }
        },
        "bitflags": [0] * 512,
    }
