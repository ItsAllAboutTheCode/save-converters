"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class PlayerData(TypedDict):
    mVersion: int
    mOperation: int
    mHoldDush: bool


class PLAYER_SAVE_DATA(TypedDict):
    mPlayerData: PlayerData


def create_player_save_data_save_dict() -> PLAYER_SAVE_DATA:
    return {"mPlayerData": {"mVersion": 0, "mOperation": 1, "mHoldDush": False}}


create_player0_save_dict = create_player_save_data_save_dict
create_player1_save_dict = create_player_save_data_save_dict
create_player2_save_dict = create_player_save_data_save_dict
create_player3_save_dict = create_player_save_data_save_dict
