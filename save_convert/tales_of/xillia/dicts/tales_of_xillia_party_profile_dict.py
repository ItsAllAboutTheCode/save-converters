"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class ScenarioEncounterCount(TypedDict):
    ScenarioFlag: int
    Count: int


class PartyProfileData(TypedDict):
    mVersion: int
    mTotalPlayTime: int
    mCurrentPlayTime: int
    mGald: int
    mCurrentSubEventListNo: int
    mMapStayTime: int
    mOverLimits: float
    mCurrentEventListNo: int
    mShopBuildPoint: list[int]
    mShopBuildLevel: list[int]
    mPrevShopBuildBonusTime: int
    mShopBuildBonus: list[int]
    mShopBuildBonusKind: list[int]
    mBottle: int
    mGradeShopFlag: list[int]
    mOnOffGradeShopFlag: list[int]
    mFameFlag: list[int]
    mGameClearCountJUR: int
    mOverLimitsCondition: int
    mActiveCookItemId: int
    mRemainCookBattleCount: int
    mUpdateShopBuildBonusFlag: bool
    mBattleShopBuildBonusJudgePercent: int
    mNextShopBuildBonus: list[int]
    mNextShopBuildBonusKind: list[int]
    mAutoItemEnable: bool
    mFameGetRequestFlag: list[int]
    mEncounterCount: int
    mGameClearCountMIR: int
    mBattleResultFlag: list[int]
    mBeforeCookItemId: int
    mTotalWorldMapJumpCount: int
    mDetailWorldMapJumpCount: int
    mScenarioEncounterCount: list[ScenarioEncounterCount]
    mBattleResultDialogueCount: int
    mLocationStayTime: int
    mTotalBlackFeatherCount: int


class EventListData(TypedDict):
    mOpenBitFlag: list[int]
    mUpdateBitFlag: list[int]
    mNewBitFlag: list[int]
    mCompleteBitFlag: list[int]
    mSynopsisOpenBitFlag: list[int]
    mViewBitFlag: list[int]


class DefeatHistoryData(TypedDict):
    mFlag: list[int]


class PartyProfileSaveDict(TypedDict):
    mPartyProfileData: PartyProfileData
    mEventListData: EventListData
    mDefeatHistoryData: DefeatHistoryData


def create_party_profile_save_dict() -> PartyProfileSaveDict:
    return {
        "mPartyProfileData": {
            "mVersion": 105,
            "mTotalPlayTime": 0,
            "mCurrentPlayTime": 0,
            "mGald": 1000,
            "mCurrentSubEventListNo": -1,
            "mMapStayTime": 70,
            "mOverLimits": 0.0,
            "mCurrentEventListNo": 60,
            "mShopBuildPoint": [0, 0, 0, 0, 0],
            "mShopBuildLevel": [1, 1, 1, 1, 1],
            "mPrevShopBuildBonusTime": 14,
            "mShopBuildBonus": [200, 200, 200, 200, 200],
            "mShopBuildBonusKind": [37, 38, 35, 40, 29],
            "mBottle": 0,
            "mGradeShopFlag": [59424, 6075] + [0] * 62,
            "mOnOffGradeShopFlag": [59424, 6075] + [0] * 62,
            "mFameFlag": [0] * 32,
            "mGameClearCountJUR": 0,
            "mOverLimitsCondition": 0,
            "mActiveCookItemId": 0,
            "mRemainCookBattleCount": 0,
            "mUpdateShopBuildBonusFlag": False,
            "mBattleShopBuildBonusJudgePercent": 1,
            "mNextShopBuildBonus": [200, 200, 200, 200, 200],
            "mNextShopBuildBonusKind": [36, 35, 40, 38, 37],
            "mAutoItemEnable": False,
            "mFameGetRequestFlag": [0] * 32,
            "mEncounterCount": 0,
            "mGameClearCountMIR": 0,
            "mBattleResultFlag": [0] * 16,
            "mBeforeCookItemId": 0,
            "mTotalWorldMapJumpCount": 0,
            "mDetailWorldMapJumpCount": 0,
            "mScenarioEncounterCount": [ScenarioEncounterCount(ScenarioFlag=0, Count=0)] * 16,
            "mBattleResultDialogueCount": 0,
            "mLocationStayTime": 70,
            "mTotalBlackFeatherCount": 0,
        },
        "mEventListData": {
            "mOpenBitFlag": [0] * 256,
            "mUpdateBitFlag": [0] * 16,
            "mNewBitFlag": [0] * 16,
            "mCompleteBitFlag": [0] * 16,
            "mSynopsisOpenBitFlag": [0] * 32,
            "mViewBitFlag": [0] * 32,
        },
        "mDefeatHistoryData": {"mFlag": [0] * 64},
    }
