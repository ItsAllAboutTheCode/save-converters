"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

import json
from typing import TypedDict

from save_convert.tales_of.tales_of_utils import COMPACT_JSON_SEPARATORS
from save_convert.tales_of.xillia.dicts.tales_of_xillia_auto_item_dict import create_auto_item_slot_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_background_music_dict import (
    create_btl_bgm_set_save_data_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_battle_book_dict import create_battle_book_new_data_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_binding_data_dict import create_binding_data_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_change_map_dict import create_change_map_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_chat_link_list_dict import create_chat_link_list_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_configuration_data_dict import (
    create_save_data_id_configuration_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_encounter_symbol_dict import create_encount_symbol_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_enemy_profile_dict import create_enemy_profile_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_event_information_dict import (
    create_event_information_save_data_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_fame_dict import create_fame_get_framework_save_data_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_item_manager_dict import (
    create_save_data_id_item_data_manager_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_key_profile_dict import (
    create_key_profile_save_dataplayer1_save_dict,
    create_key_profile_save_dataplayer2_save_dict,
    create_key_profile_save_dataplayer3_save_dict,
    create_key_profile_save_dataplayer4_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_maplink_dict import create_map_link_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_maplink_list_dict import create_map_link_list_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_npc_layout_list_dict import create_npc_layout_list_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_party_order_dict import create_party_order_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_party_profile_dict import create_party_profile_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_play_record_dict import create_play_record_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_player_save_dict import (
    create_player0_save_dict,
    create_player1_save_dict,
    create_player2_save_dict,
    create_player3_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_player_status_dict import (
    create_player1_status_save_dict,
    create_player2_status_save_dict,
    create_player3_status_save_dict,
    create_player4_status_save_dict,
    create_player5_status_save_dict,
    create_player6_status_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_scenario_dict import create_scenario_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_script_base_chat_dict import create_script_base_chat_save_dict
from save_convert.tales_of.xillia.dicts.tales_of_xillia_skill_data_dict import (
    create_save_data_id_skill_data_manager_save_dict,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_treasure_box_dict import create_treasure_box_save_dict

# Default Dictionary Create Table
SAVE_SECTION_DEFAULT_DICT_CREATOR_TABLE = [
    ("PARTY_PROFILE_SAVE_DATA", create_party_profile_save_dict),
    ("ChangeMap", create_change_map_save_dict),
    ("Scenario", create_scenario_save_dict),
    ("PLAYER_1_STATUS_SAVE_DATA", create_player1_status_save_dict),
    ("PLAYER_2_STATUS_SAVE_DATA", create_player2_status_save_dict),
    ("PLAYER_3_STATUS_SAVE_DATA", create_player3_status_save_dict),
    ("PLAYER_4_STATUS_SAVE_DATA", create_player4_status_save_dict),
    ("PLAYER_5_STATUS_SAVE_DATA", create_player5_status_save_dict),
    ("PLAYER_6_STATUS_SAVE_DATA", create_player6_status_save_dict),
    ("KEY_PROFILE_SAVE_DATAPLAYER1_0", create_key_profile_save_dataplayer1_save_dict),
    ("KEY_PROFILE_SAVE_DATAPLAYER2_0", create_key_profile_save_dataplayer2_save_dict),
    ("KEY_PROFILE_SAVE_DATAPLAYER3_0", create_key_profile_save_dataplayer3_save_dict),
    ("KEY_PROFILE_SAVE_DATAPLAYER4_0", create_key_profile_save_dataplayer4_save_dict),
    ("AUTO_ITEM_SLOT_SAVE_DATA", create_auto_item_slot_save_dict),
    ("ENEMY_PROFILE_SAVE_DATA", create_enemy_profile_save_dict),
    ("ChatLinkList", create_chat_link_list_save_dict),
    ("", lambda: None),
    ("ScriptBaseChat", create_script_base_chat_save_dict),
    ("FAME_GET_FRAMEWORK_SAVE_DATA", create_fame_get_framework_save_data_save_dict),
    ("", lambda: None),
    ("", lambda: None),
    ("BattleBookNewData", create_battle_book_new_data_save_dict),
    ("PLAYER_0_SAVE_DATA", create_player0_save_dict),
    ("PLAYER_1_SAVE_DATA", create_player1_save_dict),
    ("PLAYER_2_SAVE_DATA", create_player2_save_dict),
    ("PLAYER_3_SAVE_DATA", create_player3_save_dict),
    ("MapLink", create_map_link_save_dict),
    ("NpcLayoutList", create_npc_layout_list_save_dict),
    ("EncountSymbol", create_encount_symbol_save_dict),
    ("TreasureBox", create_treasure_box_save_dict),
    ("SAVE_DATA_ID_CONFIGURATION_DATA", create_save_data_id_configuration_save_dict),
    ("PLAY_RECORD_SAVE_DATA", create_play_record_save_dict),
    ("SAVE_DATA_ID_SKILL_DATA_MANAGER", create_save_data_id_skill_data_manager_save_dict),
    ("MapLinkList", create_map_link_list_save_dict),
    ("EVENT_INFORMATION_SAVE_DATA", create_event_information_save_data_save_dict),
    ("BindingData", create_binding_data_save_dict),
    ("SAVE_DATA_ID_ITEM_DATA_MANAGER", create_save_data_id_item_data_manager_save_dict),
    ("PARTY_ORDER_SAVE_DATA", create_party_order_save_dict),
    ("BTL_BGM_SET_SAVE_DATA", create_btl_bgm_set_save_data_save_dict),
]


# Remastered Save Dictionary defintions
# These defintions are only for the Tales of Xillia Remaastered save json
class SaveBlockEntry(TypedDict):
    Key: str
    Value: str


class XilliaRemasteredSaveDict(TypedDict):
    mSaveDataType: int
    mVersion: int
    mSaveBlockData: list[SaveBlockEntry]
    mSaveListParam: str
    mScreenCaputure: list[int]  # This typo is part of the actual remastered save structure
    mDateTime: str
    mMapID: str
    mLevel: int
    mPlayTime: int
    mRoutePartyID: int
    mIsGameClearMark: bool
    mSscenarioFlag: int  # Typo is a part of actual save structure
    mDLCUsedData: list[int]
    mDLCHaveData: list[int]


def default_remastered_save_dict() -> XilliaRemasteredSaveDict:

    save_block_list: list[SaveBlockEntry] = []
    for key, dict_creator in SAVE_SECTION_DEFAULT_DICT_CREATOR_TABLE:
        save_block_dict = dict_creator()
        value = json.dumps(save_block_dict, separators=COMPACT_JSON_SEPARATORS) if save_block_dict is not None else ""
        save_block_list.append(
            {
                "Key": key,
                "Value": value,
            }
        )

    return {
        "mSaveDataType": 0,
        "mVersion": 100,
        "mSaveBlockData": save_block_list,
        "mSaveListParam": "OI20000",
        "mScreenCaputure": [],
        "mDateTime": "2025/10/31 00:00",
        "mMapID": "DUN_INS_000",
        "mLevel": 1,
        "mPlayTime": 0,
        "mRoutePartyID": 1,
        "mIsGameClearMark": False,
        "mSscenarioFlag": 20040,
        "mDLCUsedData": [],
        "mDLCHaveData": [],
    }
