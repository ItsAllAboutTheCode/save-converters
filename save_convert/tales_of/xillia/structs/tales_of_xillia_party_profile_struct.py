"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_float, c_int32, c_uint8, c_uint16, c_uint32, c_uint64
from typing import cast, override

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    ToDictResult,
    assert_field_offset,
    assert_struct_size,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_party_profile_dict import (
    PartyProfileSaveDict,
    create_party_profile_save_dict,
)


class PARTY_PROFILE_SAVE_DATA(MarshalStructure):
    class PartyProfileData(MarshalStructure):
        class ScenarioEncounterCount(MarshalStructure):
            _fields_ = [("ScenarioFlag", c_uint32), ("Count", c_uint32)]

        _fields_ = [
            ("mVersion", c_uint32),  # offset abs=0x230
            ("__padding1__", c_uint32),  # offset abs=0x234
            ("mTotalPlayTime", c_uint64),  # offset abs=0x238
            ("mCurrentPlayTime", c_uint64),  # offset abs=0x240
            ("mGald", c_uint32),
            ("__padding2__", c_uint32),
            ("mCurrentSubEventListNo", c_uint32),
            ("mMapStayTime", c_uint32),
            ("mOverLimits", c_float),
            ("mCurrentEventListNo", c_uint32),
            ("mShopBuildPoint", c_uint32 * 5),
            ("mShopBuildLevel", c_uint32 * 5),
            ("mPrevShopBuildBonusTime", c_uint64),
            ("mShopBuildBonus", c_uint32 * 5),
            ("mShopBuildBonusKind", c_uint32 * 5),
            ("mBottle", c_uint32),
            ("mGradeShopFlag", c_uint16 * 32),
            ("mFameFlag", c_uint16 * 32),
            ("mGameClearCountJUR", c_uint32),
            ("mOverLimitsCondition", c_uint32),
            ("mActiveCookItemId", c_uint32),
            ("mRemainCookBattleCount", c_uint32),
            ("mUpdateShopBuildBonusFlag", c_bool),
            ("__padding3__", c_uint8 * 3),
            ("mBattleShopBuildBonusJudgePercent", c_uint32),
            ("mNextShopBuildBonus", c_uint32 * 5),
            ("mNextShopBuildBonusKind", c_uint32 * 5),
            ("mAutoItemEnable", c_bool),
            ("__padding4__", c_uint8 * 3),
            ("mFameGetRequestFlag", c_uint16 * 32),
            ("mEncounterCount", c_uint32),
            ("mGameClearCountMIR", c_uint32),
            ("mBattleResultFlag", c_uint32 * 16),
            ("mBeforeCookItemId", c_uint32),
            ("mTotalWorldMapJumpCount", c_uint32),
            ("mDetailWorldMapJumpCount", c_uint32),
            ("mScenarioEncounterCount", ScenarioEncounterCount * 16),
            ("mBattleResultDialogueCount", c_uint32),
            ("mLocationStayTime", c_uint64),  # offset abs=0x498
            ("mTotalBlackFeatherCount", c_uint32),  # offset rel 0x270, abs=0x4A0
            ("__align_to_4096__", c_uint8 * (0x1000 - 0x274)),  # offset rel 0x274, abs=0x4A4
        ]

    assert_struct_size(PartyProfileData, 0x1000)

    class EventListData(MarshalStructure):
        """
        NOTE: All the flags here are stored as SIGNED 32-bit ints
        """

        _fields_ = [
            ("mOpenBitFlag", c_int32 * 256),  # offset rel=0x0, abs=0x1230
            ("mUpdateBitFlag", c_int32 * 16),  # offset rel=0x400, abs=0x1630
            ("mNewBitFlag", c_int32 * 16),  # offset rel=0x440, abs=0x1670
            ("mCompleteBitFlag", c_int32 * 16),  # offset rel=0x480, abs=0x16B0
            ("mSynopsisOpenBitFlag", c_int32 * 32),  # offset rel=0x4C0, abs=0x16F0
            ("mViewBitFlag", c_int32 * 32),  # offset rel=0x540, abs=0x1770
            ("__align_to_2048__", c_uint8 * 576),  # offset rel=0x5C0, abs=0x17F0
        ]

    assert_struct_size(EventListData, 0x800)

    class DefeatHistoryData(MarshalStructure):
        """
        NOTE: Note this flag is stored UNSIGNED
        """

        _fields_ = [
            ("mFlag", c_uint32 * 64),
        ]

    assert_struct_size(DefeatHistoryData, 0x100)

    _fields_ = [
        ("mPartyProfileData", PartyProfileData),  # offset rel=0x0, abs=0x230
        ("mEventListData", EventListData),  # offset rel=0x1000, abs=0x1230
        ("mDefeatHistoryData", DefeatHistoryData),  # offset rel=0x1800, abs=0x1A30
        ("__align_to_16384__", c_uint8 * 9984),  # offset rel=0x1900, abs=0x1B30
    ]

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        The PS3 save doesn't appear to have "mOnOffGradeShopFlag" section
        So Mirror the mGradeShopFlag array to mOnOffGradeShopFlag value
        """

        party_profile_dict: PartyProfileSaveDict = create_party_profile_save_dict()
        output_dict = party_profile_dict.copy()
        dict_result = super().to_dict(skip_double_underscore_fields)

        if not dict_result or not dict_result.value:
            return dict_result

        # Merge the loaded dictionary with the default dictionary
        output_dict |= cast(PartyProfileSaveDict, cast(object, dict_result.value))
        # If the PS3 grade shop flag is set to 0, then use the default value from the Remastred save data
        if output_dict["mPartyProfileData"]["mGradeShopFlag"][:2] == [0, 0]:
            output_dict["mPartyProfileData"]["mGradeShopFlag"] = party_profile_dict["mPartyProfileData"][
                "mGradeShopFlag"
            ]
        output_dict["mPartyProfileData"]["mOnOffGradeShopFlag"] = output_dict["mPartyProfileData"]["mGradeShopFlag"]

        return ToDictResult(True, output_dict)


assert_field_offset(PARTY_PROFILE_SAVE_DATA, "mEventListData", 0x1000)
assert_field_offset(PARTY_PROFILE_SAVE_DATA, "mDefeatHistoryData", 0x1800)
assert_struct_size(PARTY_PROFILE_SAVE_DATA, 0x4000)
