"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class PartyOrderStackEntry(TypedDict):
    mPartyId: int
    mOrder: int


class PartyOrderData(TypedDict):
    mVersion: int
    mTop: int
    mOrder: list[int]
    mOrderBackup: list[int]
    mOrderStack: list[PartyOrderStackEntry]


class PARTY_ORDER_SAVE_DATA(TypedDict):
    mPartyOrderData: PartyOrderData


def create_party_order_save_dict() -> PARTY_ORDER_SAVE_DATA:
    return {
        "mPartyOrderData": {
            "mVersion": 0,
            "mTop": 2,
            "mOrder": [2] + [0] * 5,
            "mOrderBackup": [0] * 30,
            "mOrderStack": [{"mPartyId": 0, "mOrder": 0}] * 6,
        }
    }
