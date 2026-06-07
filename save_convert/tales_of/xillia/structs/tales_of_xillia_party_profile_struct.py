"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_float, c_int32, c_uint16, c_uint32, c_uint64
from typing import cast, override

from save_convert.structs.marshal_dict_base import ToDictResult
from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_party_profile_dict import (
    PartyProfileSaveDict,
    create_party_profile_save_dict,
)


class PARTY_PROFILE_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class PartyProfileData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        class ScenarioEncounterCount(FillEndianSwapStructure):  #  type: ignore[metaclass]
            _size_ = 0x8
            _offset_fields_ = [OffsetField(0x0, ("ScenarioFlag", c_uint32)), OffsetField(0x4, ("Count", c_uint32))]

        _size_ = 0x1000
        _offset_fields_ = [
            OffsetField(0x0, ("mVersion", c_uint32)),  # offset abs=0x230
            OffsetField(0x8, ("mTotalPlayTime", c_uint64)),  # offset abs=0x238
            OffsetField(0x10, ("mCurrentPlayTime", c_uint64)),  # offset abs=0x240
            OffsetField(0x18, ("mGald", c_uint32)),  # offset abs=0x248
            OffsetField(0x1C, ("mCurrentSubEventListNo", c_uint32)),  # offset abs=0x24C
            OffsetField(0x20, ("mMapStayTime", c_uint64)),  # offset abs=0x250
            OffsetField(0x28, ("mOverLimits", c_float)),  # offset abs=0x258
            OffsetField(0x2C, ("mCurrentEventListNo", c_uint32)),  # offset abs=0x25C
            OffsetField(0x30, ("mShopBuildPoint", c_uint32 * 5)),  # offset abs=0x260
            OffsetField(0x44, ("mShopBuildLevel", c_uint32 * 5)),  # offset abs=0x274
            OffsetField(0x58, ("mPrevShopBuildBonusTime", c_uint64)),  # offset abs=0x288
            OffsetField(0x60, ("mShopBuildBonus", c_uint32 * 5)),  # offset abs=0x290
            OffsetField(0x74, ("mShopBuildBonusKind", c_uint32 * 5)),  # offset abs=0x2A4
            OffsetField(0x88, ("mBottle", c_uint32)),  # offset abs=0x2B8
            OffsetField(0x8C, ("mGradeShopFlag", c_uint16 * 32)),  # offset abs=0x2BC
            OffsetField(0xCC, ("mFameFlag", c_uint16 * 32)),  # offset abs=0x2FC
            OffsetField(0x10C, ("mGameClearCountJUR", c_uint32)),  # offset abs=0x33C
            OffsetField(0x110, ("mOverLimitsCondition", c_uint32)),  # offset abs=0x340
            OffsetField(0x114, ("mActiveCookItemId", c_uint32)),  # offset abs=0x344
            OffsetField(0x118, ("mRemainCookBattleCount", c_uint32)),  # offset abs=0x348
            OffsetField(0x11C, ("mUpdateShopBuildBonusFlag", c_bool)),  # offset abs=0x34C
            OffsetField(0x120, ("mBattleShopBuildBonusJudgePercent", c_uint32)),  # offset abs=0x350
            OffsetField(0x124, ("mNextShopBuildBonus", c_uint32 * 5)),  # offset abs=0x354
            OffsetField(0x138, ("mNextShopBuildBonusKind", c_uint32 * 5)),  # offset abs=0x368
            OffsetField(0x14C, ("mAutoItemEnable", c_bool)),  # offset abs=0x37C
            OffsetField(0x150, ("mFameGetRequestFlag", c_uint16 * 32)),  # offset abs=0x380
            OffsetField(0x190, ("mEncounterCount", c_uint32)),  # offset abs=0x3C0
            OffsetField(0x194, ("mGameClearCountMIR", c_uint32)),  # offset abs=0x3C4
            OffsetField(0x198, ("mBattleResultFlag", c_uint32 * 16)),  # offset abs=0x4C8
            OffsetField(0x1D8, ("mBeforeCookItemId", c_uint32)),  # offset abs=0x408
            OffsetField(0x1DC, ("mTotalWorldMapJumpCount", c_uint32)),  # offset abs=0x40C
            OffsetField(0x1E0, ("mDetailWorldMapJumpCount", c_uint32)),  # offset abs=0x410
            OffsetField(0x1E4, ("mScenarioEncounterCount", ScenarioEncounterCount * 16)),  #  type: ignore[arg-type,operator] # offset abs=0x414
            OffsetField(0x264, ("mBattleResultDialogueCount", c_uint32)),  # offset abs=0x494
            OffsetField(0x268, ("mLocationStayTime", c_uint64)),  # offset abs=0x498
            OffsetField(0x270, ("mTotalBlackFeatherCount", c_uint32)),  # offset rel 0x270, abs=0x4A0
        ]

    class EventListData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        """
        NOTE: All the flags here are stored as SIGNED 32-bit ints
        """

        _size_ = 0x800
        _offset_fields_ = [
            OffsetField(0x0, ("mOpenBitFlag", c_int32 * 256)),  # offset rel=0x0, abs=0x1230
            OffsetField(0x400, ("mUpdateBitFlag", c_int32 * 16)),  # offset rel=0x400, abs=0x1630
            OffsetField(0x440, ("mNewBitFlag", c_int32 * 16)),  # offset rel=0x440, abs=0x1670
            OffsetField(0x480, ("mCompleteBitFlag", c_int32 * 16)),  # offset rel=0x480, abs=0x16B0
            OffsetField(0x4C0, ("mSynopsisOpenBitFlag", c_int32 * 32)),  # offset rel=0x4C0, abs=0x16F0
            OffsetField(0x540, ("mViewBitFlag", c_int32 * 32)),  # offset rel=0x540, abs=0x1770
        ]

    class DefeatHistoryData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        """
        NOTE: Note this flag is stored UNSIGNED
        """

        _size_ = 0x100
        _offset_fields_ = [
            OffsetField(0x0, ("mFlag", c_uint32 * 64)),
        ]

    _size_ = 0x4000
    _offset_fields_ = [
        OffsetField(0x0, ("mPartyProfileData", PartyProfileData)),  # offset rel=0x0, abs=0x230
        OffsetField(0x1000, ("mEventListData", EventListData)),  # offset rel=0x1000, abs=0x1230
        OffsetField(0x1800, ("mDefeatHistoryData", DefeatHistoryData)),  # offset rel=0x1800, abs=0x1A30
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


assert_struct_no_padding(PARTY_PROFILE_SAVE_DATA)
