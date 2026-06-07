"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

import json
import logging
import sys
from ctypes import Array, c_char, c_uint8, c_uint16, c_uint32
from typing import NamedTuple, cast, override

from save_convert.structs.marshal_byte_base import FromBytesResult, MarshalStructByteBase
from save_convert.structs.marshal_dict_base import ToDictResult
from save_convert.structs.marshal_struct_base import ByteorderLiteral, assert_struct_size
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    MarshalStructure,
    OffsetField,
)
from save_convert.tales_of.tales_of_utils import COMPACT_JSON_SEPARATORS
from save_convert.tales_of.xillia.structs.tales_of_xillia_auto_item_struct import AUTO_ITEM_SLOT_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_change_map_struct import ChangeMap
from save_convert.tales_of.xillia.structs.tales_of_xillia_chat_link_list_struct import ChatLinkList
from save_convert.tales_of.xillia.structs.tales_of_xillia_configuration_data_struct import (
    SAVE_DATA_ID_CONFIGURATION_DATA,
)
from save_convert.tales_of.xillia.structs.tales_of_xillia_encounter_symbol_struct import EncountSymbol
from save_convert.tales_of.xillia.structs.tales_of_xillia_enemy_profile_struct import ENEMY_PROFILE_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_event_information_struct import EVENT_INFORMATION_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_fame_struct import FAME_GET_FRAMEWORK_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_item_manager_struct import SAVE_DATA_ID_ITEM_DATA_MANAGER
from save_convert.tales_of.xillia.structs.tales_of_xillia_key_profile_struct import KEY_PROFILE_SAVE_DATAPLAYER
from save_convert.tales_of.xillia.structs.tales_of_xillia_maplink_list_struct import MapLinkList
from save_convert.tales_of.xillia.structs.tales_of_xillia_maplink_struct import MapLink
from save_convert.tales_of.xillia.structs.tales_of_xillia_npc_layout_list_struct import NpcLayoutList
from save_convert.tales_of.xillia.structs.tales_of_xillia_party_order_struct import PARTY_ORDER_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_party_profile_struct import PARTY_PROFILE_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_play_record_struct import PLAY_RECORD_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_player_save_struct import PLAYER_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_player_status_struct import PLAYER_STATUS_SAVE_DATA
from save_convert.tales_of.xillia.structs.tales_of_xillia_scenario_struct import Scenario
from save_convert.tales_of.xillia.structs.tales_of_xillia_treasure_box_struct import TreasureBox
from save_convert.tales_of.xillia.tales_of_xillia_dicts import SaveBlockEntry, default_remastered_save_dict

LOGGER = logging.getLogger("xillia_structs")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

# Save size of Xillia PS3 save
XILLIA_PS3_SAVE_SIZE = 453760

XILLIA_PS3_SAVE_VERSION = 100
XILLIA_PS3_SAVE_SECTION_ENTRY_COUNT = 34
XILLIA_PS3_SAVE_DATA_TYPE = 1


class SaveSectionTuple(NamedTuple):
    name: str
    name_offset: int
    data_offset: int
    data_size: int


# Map information about each save section offset within the binary PS3 save
SAVE_SECTIONS_TUPLE: list[SaveSectionTuple] = [
    SaveSectionTuple("PARTY_PROFILE_SAVE_DATA", 0x6E9D0, 0x230, 0x4000),
    SaveSectionTuple("ChangeMap", 0x6E9E8, 0x4230, 0x40),
    SaveSectionTuple("Scenario", 0x6E9F2, 0x4270, 0x4280),
    SaveSectionTuple("PLAYER_1_STATUS_SAVE_DATA", 0x6E9FB, 0x84F0, 0xA000),
    SaveSectionTuple("PLAYER_2_STATUS_SAVE_DATA", 0x6EA15, 0x124F0, 0xA000),
    SaveSectionTuple("PLAYER_3_STATUS_SAVE_DATA", 0x6EA2F, 0x1C4F0, 0xA000),
    SaveSectionTuple("PLAYER_4_STATUS_SAVE_DATA", 0x6EA49, 0x264F0, 0xA000),
    SaveSectionTuple("PLAYER_5_STATUS_SAVE_DATA", 0x6EA63, 0x304F0, 0xA000),
    SaveSectionTuple("PLAYER_6_STATUS_SAVE_DATA", 0x6EA7D, 0x3A4F0, 0xA000),
    SaveSectionTuple("KEY_PROFILE_SAVE_DATAPLAYER1_0", 0x6EA97, 0x444F0, 0x1000),
    SaveSectionTuple("KEY_PROFILE_SAVE_DATAPLAYER2_0", 0x6EAB6, 0x454F0, 0x1000),
    SaveSectionTuple("KEY_PROFILE_SAVE_DATAPLAYER3_0", 0x6EAD5, 0x464F0, 0x1000),
    SaveSectionTuple("KEY_PROFILE_SAVE_DATAPLAYER4_0", 0x6EAF4, 0x474F0, 0x1000),
    SaveSectionTuple("PLAY_RECORD_SAVE_DATA", 0x6EB13, 0x484F0, 0x4000),
    SaveSectionTuple("FAME_GET_FRAMEWORK_SAVE_DATA", 0x6EB29, 0x4C4F0, 0x0),
    SaveSectionTuple("", 0x6EB46, 0x4C4F0, 0x0),
    SaveSectionTuple("PLAYER_0_SAVE_DATA", 0x6EB47, 0x4C4F0, 0x4000),
    SaveSectionTuple("PLAYER_1_SAVE_DATA", 0x6EB5A, 0x504F0, 0x4000),
    SaveSectionTuple("PLAYER_2_SAVE_DATA", 0x6EB6D, 0x544F0, 0x4000),
    SaveSectionTuple("PLAYER_3_SAVE_DATA", 0x6EB80, 0x584F0, 0x4000),
    SaveSectionTuple("MapLink", 0x6EB93, 0x5C4F0, 0x80),
    SaveSectionTuple("MapLinkList", 0x6EB9B, 0x5C570, 0x04),
    SaveSectionTuple("NpcLayoutList", 0x6EBA7, 0x5C580, 0x800),
    SaveSectionTuple("EncountSymbol", 0x6EBB5, 0x5CD80, 0x1440),
    SaveSectionTuple("TreasureBox", 0x6EBC3, 0x5E1C0, 0x1E04),
    SaveSectionTuple("ChatLinkList", 0x6EBCF, 0x5FFD0, 0x200),
    SaveSectionTuple("", 0x6EBDC, 0x601D0, 0x0),
    SaveSectionTuple("SAVE_DATA_ID_ITEM_DATA_MANAGER", 0x6EBDD, 0x601D0, 0x4000),
    SaveSectionTuple("", 0x6EBFC, 0x641D0, 0x0),
    SaveSectionTuple("EVENT_INFORMATION_SAVE_DATA", 0x6EBFD, 0x641D0, 0x0),
    SaveSectionTuple("AUTO_ITEM_SLOT_SAVE_DATA", 0x6EC19, 0x641D0, 0x800),
    SaveSectionTuple("ENEMY_PROFILE_SAVE_DATA", 0x6EC32, 0x649D0, 0x5000),
    SaveSectionTuple("SAVE_DATA_ID_CONFIGURATION_DATA", 0x6EC4A, 0x699D0, 0x1000),
    SaveSectionTuple("PARTY_ORDER_SAVE_DATA", 0x6EC6A, 0x6A9D0, 0x4000),
]


SAVE_SECTIONS = [section_tup[0] for section_tup in SAVE_SECTIONS_TUPLE]

SAVE_SECTION_TO_CLASS_TABLE = {
    "PARTY_PROFILE_SAVE_DATA": PARTY_PROFILE_SAVE_DATA,
    "ChangeMap": ChangeMap,
    "Scenario": Scenario,
    "PLAYER_1_STATUS_SAVE_DATA": PLAYER_STATUS_SAVE_DATA,
    "PLAYER_2_STATUS_SAVE_DATA": PLAYER_STATUS_SAVE_DATA,
    "PLAYER_3_STATUS_SAVE_DATA": PLAYER_STATUS_SAVE_DATA,
    "PLAYER_4_STATUS_SAVE_DATA": PLAYER_STATUS_SAVE_DATA,
    "PLAYER_5_STATUS_SAVE_DATA": PLAYER_STATUS_SAVE_DATA,
    "PLAYER_6_STATUS_SAVE_DATA": PLAYER_STATUS_SAVE_DATA,
    "KEY_PROFILE_SAVE_DATAPLAYER1_0": KEY_PROFILE_SAVE_DATAPLAYER,
    "KEY_PROFILE_SAVE_DATAPLAYER2_0": KEY_PROFILE_SAVE_DATAPLAYER,
    "KEY_PROFILE_SAVE_DATAPLAYER3_0": KEY_PROFILE_SAVE_DATAPLAYER,
    "KEY_PROFILE_SAVE_DATAPLAYER4_0": KEY_PROFILE_SAVE_DATAPLAYER,
    "PLAY_RECORD_SAVE_DATA": PLAY_RECORD_SAVE_DATA,
    "PLAYER_0_SAVE_DATA": PLAYER_SAVE_DATA,
    "PLAYER_1_SAVE_DATA": PLAYER_SAVE_DATA,
    "PLAYER_2_SAVE_DATA": PLAYER_SAVE_DATA,
    "PLAYER_3_SAVE_DATA": PLAYER_SAVE_DATA,
    "MapLink": MapLink,
    "MapLinkList": MapLinkList,
    "NpcLayoutList": NpcLayoutList,
    "EncountSymbol": EncountSymbol,
    "TreasureBox": TreasureBox,
    "ChatLinkList": ChatLinkList,
    "SAVE_DATA_ID_ITEM_DATA_MANAGER": SAVE_DATA_ID_ITEM_DATA_MANAGER,
    "AUTO_ITEM_SLOT_SAVE_DATA": AUTO_ITEM_SLOT_SAVE_DATA,
    "ENEMY_PROFILE_SAVE_DATA": ENEMY_PROFILE_SAVE_DATA,
    "SAVE_DATA_ID_CONFIGURATION_DATA": SAVE_DATA_ID_CONFIGURATION_DATA,
    "PARTY_ORDER_SAVE_DATA": PARTY_ORDER_SAVE_DATA,
    "FAME_GET_FRAMEWORK_SAVE_DATA": None,
    "EVENT_INFORMATION_SAVE_DATA": None,
    "": None,
}


class XilliaSaveSectionEntry(MarshalStructure):
    _fields_ = [
        ("save_section_key_offset", c_uint32),
        ("save_section_data_offset", c_uint32),
        ("save_section_data_size", c_uint32),
        ("padding", c_uint32),
    ]


assert_struct_size(XilliaSaveSectionEntry, 0x10)


class XilliaSaveSectionHeader(MarshalStructure):
    _fields_ = [
        ("mVersion", c_uint16),
        ("mSaveBlockCount", c_uint16),
        ("mSaveFileTotalSize", c_uint32),
        ("mSaveDataType", c_uint8),
        ("__padding_bytes", c_uint8 * 3),
        ("__padding_int__", c_uint32),
    ]

    def __init__(self):
        """Initializes the Save Section Lookup Table for"""
        super().__init__()
        setattr(self, "mVersion", XILLIA_PS3_SAVE_VERSION)
        setattr(self, "mSaveBlockCount", XILLIA_PS3_SAVE_SECTION_ENTRY_COUNT)
        setattr(self, "mSaveFileTotalSize", XILLIA_PS3_SAVE_SIZE)
        setattr(self, "mSaveDataType", XILLIA_PS3_SAVE_DATA_TYPE)


assert_struct_size(XilliaSaveSectionHeader, 0x10)


class XilliaSaveBlockStringTable(MarshalStructure):
    # Create an bytes array that can fir the save section name + 1 for the NUL-terminator
    _fields_ = [(name, c_char * (len(name) + 1)) for name in SAVE_SECTIONS]

    def __init__(self):
        """Initializes the Save Section Lookup Table for strings to containing the strings"""
        super().__init__()
        for name in SAVE_SECTIONS:
            setattr(self, name, name.encode("utf-8"))


assert_struct_size(XilliaSaveSectionHeader, 0x10)


class EmptySection(MarshalStructure):
    _fields_ = []


class XilliaSaveStruct(FillEndianSwapStructure):  # type: ignore[metaclass]
    """
    Structure providing a mapping for the entire Tales of Xillia raw save file
    """

    _size_ = XILLIA_PS3_SAVE_SIZE
    _offset_fields_ = [
        OffsetField(0x0, ("Header", XilliaSaveSectionHeader)),
        OffsetField(0x10, ("SaveSectionLookupTable", XilliaSaveSectionEntry * XILLIA_PS3_SAVE_SECTION_ENTRY_COUNT)),
        OffsetField(SAVE_SECTIONS_TUPLE[0].data_offset, ("PARTY_PROFILE_SAVE_DATA", PARTY_PROFILE_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[1].data_offset, ("ChangeMap", ChangeMap)),
        OffsetField(SAVE_SECTIONS_TUPLE[2].data_offset, ("Scenario", Scenario)),
        OffsetField(SAVE_SECTIONS_TUPLE[3].data_offset, ("PLAYER_1_STATUS_SAVE_DATA", PLAYER_STATUS_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[4].data_offset, ("PLAYER_2_STATUS_SAVE_DATA", PLAYER_STATUS_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[5].data_offset, ("PLAYER_3_STATUS_SAVE_DATA", PLAYER_STATUS_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[6].data_offset, ("PLAYER_4_STATUS_SAVE_DATA", PLAYER_STATUS_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[7].data_offset, ("PLAYER_5_STATUS_SAVE_DATA", PLAYER_STATUS_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[8].data_offset, ("PLAYER_6_STATUS_SAVE_DATA", PLAYER_STATUS_SAVE_DATA)),
        OffsetField(
            SAVE_SECTIONS_TUPLE[9].data_offset, ("KEY_PROFILE_SAVE_DATAPLAYER1_0", KEY_PROFILE_SAVE_DATAPLAYER)
        ),
        OffsetField(
            SAVE_SECTIONS_TUPLE[10].data_offset, ("KEY_PROFILE_SAVE_DATAPLAYER2_0", KEY_PROFILE_SAVE_DATAPLAYER)
        ),
        OffsetField(
            SAVE_SECTIONS_TUPLE[11].data_offset, ("KEY_PROFILE_SAVE_DATAPLAYER3_0", KEY_PROFILE_SAVE_DATAPLAYER)
        ),
        OffsetField(
            SAVE_SECTIONS_TUPLE[12].data_offset, ("KEY_PROFILE_SAVE_DATAPLAYER4_0", KEY_PROFILE_SAVE_DATAPLAYER)
        ),
        OffsetField(SAVE_SECTIONS_TUPLE[13].data_offset, ("PLAY_RECORD_SAVE_DATA", PLAY_RECORD_SAVE_DATA)),
        OffsetField(
            SAVE_SECTIONS_TUPLE[14].data_offset, ("FAME_GET_FRAMEWORK_SAVE_DATA", FAME_GET_FRAMEWORK_SAVE_DATA)
        ),
        OffsetField(SAVE_SECTIONS_TUPLE[15].data_offset, ("__empty_section_1__", EmptySection)),
        OffsetField(SAVE_SECTIONS_TUPLE[16].data_offset, ("PLAYER_0_SAVE_DATA", PLAYER_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[17].data_offset, ("PLAYER_1_SAVE_DATA", PLAYER_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[18].data_offset, ("PLAYER_2_SAVE_DATA", PLAYER_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[19].data_offset, ("PLAYER_3_SAVE_DATA", PLAYER_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[20].data_offset, ("MapLink", MapLink)),
        OffsetField(SAVE_SECTIONS_TUPLE[21].data_offset, ("MapLinkList", MapLinkList)),
        OffsetField(SAVE_SECTIONS_TUPLE[22].data_offset, ("NpcLayoutList", NpcLayoutList)),
        OffsetField(SAVE_SECTIONS_TUPLE[23].data_offset, ("EncountSymbol", EncountSymbol)),
        OffsetField(SAVE_SECTIONS_TUPLE[24].data_offset, ("TreasureBox", TreasureBox)),
        OffsetField(SAVE_SECTIONS_TUPLE[25].data_offset, ("ChatLinkList", ChatLinkList)),
        OffsetField(SAVE_SECTIONS_TUPLE[26].data_offset, ("__empty_section_2__", EmptySection)),
        OffsetField(
            SAVE_SECTIONS_TUPLE[27].data_offset, ("SAVE_DATA_ID_ITEM_DATA_MANAGER", SAVE_DATA_ID_ITEM_DATA_MANAGER)
        ),
        OffsetField(SAVE_SECTIONS_TUPLE[28].data_offset, ("__empty_section_3__", EmptySection)),
        OffsetField(SAVE_SECTIONS_TUPLE[29].data_offset, ("EVENT_INFORMATION_SAVE_DATA", EVENT_INFORMATION_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[30].data_offset, ("AUTO_ITEM_SLOT_SAVE_DATA", AUTO_ITEM_SLOT_SAVE_DATA)),
        OffsetField(SAVE_SECTIONS_TUPLE[31].data_offset, ("ENEMY_PROFILE_SAVE_DATA", ENEMY_PROFILE_SAVE_DATA)),
        OffsetField(
            SAVE_SECTIONS_TUPLE[32].data_offset, ("SAVE_DATA_ID_CONFIGURATION_DATA", SAVE_DATA_ID_CONFIGURATION_DATA)
        ),
        OffsetField(SAVE_SECTIONS_TUPLE[33].data_offset, ("PARTY_ORDER_SAVE_DATA", PARTY_ORDER_SAVE_DATA)),
        # The following field is the save section string table
        OffsetField(0x6E9D0, ("SaveBlockStringTable", XilliaSaveBlockStringTable)),
    ]

    def __init__(self):
        """Initializes the save section header as well
        as each save section entry

        This required when converting a save back to PS3 format
        """
        super().__init__()

        setattr(self, "Header", XilliaSaveSectionHeader())
        save_section_table = cast(Array[XilliaSaveSectionEntry], getattr(self, "SaveSectionLookupTable"))
        for index, save_section_entry in enumerate(save_section_table):
            save_section_entry = cast(XilliaSaveSectionEntry, save_section_entry)
            setattr(save_section_entry, "save_section_key_offset", SAVE_SECTIONS_TUPLE[index].name_offset)
            setattr(save_section_entry, "save_section_data_offset", SAVE_SECTIONS_TUPLE[index].data_offset)
            setattr(save_section_entry, "save_section_data_size", SAVE_SECTIONS_TUPLE[index].data_size)

        setattr(self, "SaveBlockStringTable", XilliaSaveBlockStringTable())

    @override
    @staticmethod
    def from_bytes[T: MarshalStructByteBase](
        input_data: memoryview, struct_type: type[T], byteorder: ByteorderLiteral = "big"
    ) -> FromBytesResult[T]:
        """
        Convert entire Xillia PS3 save data to a struct
        """
        xillia_section_table_result = XilliaSaveSectionHeader.from_bytes(
            memoryview(input_data), XilliaSaveSectionHeader, byteorder="big"
        )
        if (
            not xillia_section_table_result
            or not xillia_section_table_result.value
            or not xillia_section_table_result.next_memoryview
        ):
            LOGGER.error(f"Failed to marshal bytes into {XilliaSaveSectionHeader.__name__} struct")
            return FromBytesResult(False, input_data)

        xillia_section_table = xillia_section_table_result.value
        save_block_count = getattr(xillia_section_table, "mSaveBlockCount")
        if save_block_count is None:
            LOGGER.error(f'Unable to find "mSaveBlockCount" attribute on struct {xillia_section_table}')
            return FromBytesResult(False, xillia_section_table_result.next_memoryview)

        # Create the struct instance at this point
        struct_inst = struct_type()

        # NOTE: Set the "Header" field to the loaded save section header
        setattr(struct_inst, "Header", xillia_section_table)
        save_section_lookup_table: list[XilliaSaveSectionEntry] = getattr(struct_inst, "SaveSectionLookupTable")

        section_entry_view = xillia_section_table_result.next_memoryview

        for index in range(save_block_count):
            xillia_section_entry_result = XilliaSaveSectionEntry.from_bytes(
                section_entry_view, XilliaSaveSectionEntry, byteorder="big"
            )
            if not xillia_section_entry_result or not xillia_section_entry_result.value:
                LOGGER.error(f"Failed reading section entry {index} for Xillia PS3 save")
                return FromBytesResult(False, xillia_section_entry_result.next_memoryview)

            # Update the save section entry view to point to the next entry
            section_entry_view = cast(memoryview, xillia_section_entry_result.next_memoryview)

            xillia_section_entry = xillia_section_entry_result.value
            # NOTE: Set the "SaveSectionLookupTable" field array entry to the loaded save section entry
            save_section_lookup_table[index] = xillia_section_entry

            save_section_key_off = cast(int, getattr(xillia_section_entry, "save_section_key_offset"))
            save_section_data_off = cast(int, getattr(xillia_section_entry, "save_section_data_offset"))
            save_section_data_size = cast(int, getattr(xillia_section_entry, "save_section_data_size"))

            # Lookup the name of the save section
            # It is a null-terminated string so such for NULL
            save_section_name_view = memoryview(input_data)[save_section_key_off:]
            try:
                null_term_index = save_section_name_view.index(0)  # type: ignore[misc]
                save_section_name = save_section_name_view[:null_term_index].tobytes().decode("utf-8")
            except ValueError:
                LOGGER.warning(
                    f"Save section key at offset {save_section_key_off} in PS3 save file"
                    " is not NUL-terminated. The key will be assumed to go to the end of the save file"
                )
                save_section_name = save_section_name_view.tobytes().decode("utf-8")

            save_section_type = SAVE_SECTION_TO_CLASS_TABLE.get(save_section_name)
            if not save_section_type:
                LOGGER.debug(
                    f"Save section {save_section_key_off} offset has no associated c structure,"
                    " as it has size struct size of 0. Continuing to next section..."
                )
                continue

            # Load the Save section structure from bytes
            save_section_data_view = memoryview(input_data)[
                save_section_data_off : save_section_data_off + save_section_data_size
            ]
            from_bytes_result = save_section_type.from_bytes(save_section_data_view, save_section_type, byteorder="big")
            if not from_bytes_result or not from_bytes_result.value:
                LOGGER.error(f"Failed to load data for {save_section_name} has no associated c structure. Aborting...")
                return FromBytesResult(False, section_entry_view)

            # NOTE: Set the save section to the loaded struct type
            setattr(struct_inst, save_section_name, from_bytes_result.value)

        return FromBytesResult(True, section_entry_view, struct_inst)

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Convert entire Xillia save data to a dictionary compatible with the Remaster save format

        The Save JSON other fields are augmented with values from the structure
        """

        # Store the Save section struct as a dict
        remaster_save_dict = default_remastered_save_dict()
        # build a save block section key name to index map to quickly lookup existing entries

        # The binary save file contains section with a empty string name ""
        # map that to the struct __empty_section_<N>__ key
        section_name_index_table = {}
        empty_index = 1
        for index, save_block in enumerate(remaster_save_dict["mSaveBlockData"]):
            save_section_name = save_block["Key"] if save_block["Key"] else f"__empty_section_{empty_index}__"
            section_name_index_table[save_section_name] = index
            empty_index += 1

        # reset empty index to 1
        empty_index = 1
        for save_section_name in SAVE_SECTIONS:
            if not save_section_name:
                # The binary save file contains section with a empty string name ""
                # map that to the struct __empty_section_<N>__ key
                save_section_name = f"__empty_section_{empty_index}__"
                empty_index += 1

            save_section_struct: MarshalStructure | None = getattr(self, save_section_name, None)
            if not save_section_struct:
                LOGGER.error(f"Save struct is missing required section '{save_section_name}'")
                return ToDictResult(False)

            to_dict_result = save_section_struct.to_dict()
            if to_dict_result and to_dict_result.value:
                if (save_section_index := section_name_index_table.get(save_section_name, None)) is not None:
                    remaster_save_dict["mSaveBlockData"][save_section_index] = SaveBlockEntry(
                        Key=save_section_name,
                        Value=json.dumps(to_dict_result.value, separators=COMPACT_JSON_SEPARATORS),
                    )
                else:
                    remaster_save_dict["mSaveBlockData"].append(
                        SaveBlockEntry(
                            Key=save_section_name,
                            Value=json.dumps(to_dict_result.value, separators=COMPACT_JSON_SEPARATORS),
                        )
                    )

        # Now update the extra fields in the JSON format.
        # mSaveDataType, mMapID, mLevel, mPlayTime, mRoutePartyID, mISGameClearMark,
        # mSscenarioFlag, mDLCHaveData

        # For the save type 0 is normal save, 1 is auto save, 2 is quick save
        # remaster_save_dict["mSaveDataType"] = self.Header.mSaveDataType
        remaster_save_dict["mMapID"] = self.Scenario.map.decode("utf-8")
        # Route 1 is Jude, Route 2 is Milla
        remaster_save_dict["mLevel"] = (
            self.PLAYER_1_STATUS_SAVE_DATA.mPlayerStatusData.mStatus.level
            if self.Scenario.route == 1
            else self.PLAYER_1_STATUS_SAVE_DATA.mPlayerStatusData.mStatus.level
        )
        remaster_save_dict["mPlayTime"] = self.PARTY_PROFILE_SAVE_DATA.mPartyProfileData.mTotalPlayTime
        remaster_save_dict["mRoutePartyID"] = self.Scenario.route
        remaster_save_dict["mIsGameClearMark"] = bool(
            self.PARTY_PROFILE_SAVE_DATA.mPartyProfileData.mGameClearCountJUR
            or self.PARTY_PROFILE_SAVE_DATA.mPartyProfileData.mGameClearCountMIR
        )
        remaster_save_dict["mSscenarioFlag"] = self.Scenario.flag

        # Do NOT set the "mDLCUsedData" field in case the user doesn't have the DLC on the Remastered Game version
        remaster_save_dict["mDLCHaveData"] += self.SAVE_DATA_ID_ITEM_DATA_MANAGER.mDLCCheckItemID.mItemIDArray

        return ToDictResult(True, remaster_save_dict)


assert_struct_size(XilliaSaveStruct, XILLIA_PS3_SAVE_SIZE)
