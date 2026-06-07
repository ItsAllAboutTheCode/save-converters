"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_char, c_float, c_uint8, c_uint16, c_uint32
from typing import cast, override

from save_convert.structs.marshal_dict_base import ToDictResult
from save_convert.structs.marshal_struct_base import assert_field_offset, assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_player_status_dict import (
    PlayerStatusSaveDataDict,
    create_player1_status_save_dict,
)
from save_convert.tales_of.xillia.structs.tales_of_xillia_math_structs import Color, Matrix, Vector2i


class PLAYER_STATUS_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    """
    Note the PS3 save stores the "formationIndex: field as two uint32_t objects
    while the Remaster save stores it as a Vector2f (two floats)
    """

    class PlayerStatusData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        class PlayerStatus(FillEndianSwapStructure):  #  type: ignore[metaclass]
            _size_ = 0x2768
            _offset_fields_ = [
                OffsetField(0x0, ("bParty", c_bool)),  # char 1 offset abs=0x8500
                OffsetField(0x4, ("partyID", c_uint32)),  # char 1 offset abs=0x8504
                OffsetField(0x8, ("level", c_uint32)),  # char 1 offset abs=0x8508
                OffsetField(0xC, ("hp", c_uint32)),  # char 1 offset abs=0x850C
                OffsetField(0x10, ("tp", c_uint32)),  # char 1 offset abs=0x8510
                OffsetField(0x14, ("ac", c_uint32)),  # char 1 offset abs=0x8514
                OffsetField(0x20, ("baseHPMax", c_uint32)),  # char 1 offset abs=0x8520
                OffsetField(0x24, ("baseTPMax", c_uint32)),  # char 1 offset abs=0x8524
                OffsetField(0x28, ("baseACMax", c_uint32)),  # char 1 offset abs=0x8528
                OffsetField(0x2C, ("baseSPMax", c_uint32)),  # char 1 offset abs=0x852C
                OffsetField(0x30, ("baseStrength", c_uint32)),  # char 1 offset abs=0x8530
                OffsetField(0x34, ("baseIntelligence", c_uint32)),  # char 1 offset abs=0x8534
                OffsetField(0x38, ("baseStamina", c_uint32)),  # char 1 offset abs=0x8538
                OffsetField(0x3C, ("baseDexterity", c_uint32)),  # char 1 offset abs=0x853C
                OffsetField(0x40, ("baseAgility", c_uint32)),  # char 1 offset abs=0x8540
                OffsetField(0x44, ("baseSpirit", c_uint32)),  # char 1 offset abs=0x8544
                OffsetField(0x48, ("baseLuck", c_uint32)),  # char 1 offset abs=0x8548
                OffsetField(0x4C, ("elementEndurance", c_float * 6)),  # char 1 offset abs=0x854C
                OffsetField(0x64, ("equipment", c_uint32 * 4)),  # char 1 offset abs=0x8564
                OffsetField(0x74, ("magicArtsLearn", c_uint32 * 64)),  # char 1 offset abs=0x8574
                OffsetField(0x174, ("magicArtsEnable", c_uint32 * 64)),  # char 1 offset abs=0x8674
                OffsetField(0x274, ("magicArtsCount", c_uint32 * 2048)),  # char 1 offset abs=0x8774
                OffsetField(0x2274, ("skillLearn", c_uint32 * 32)),  # char 1 offset abs=0xA774
                OffsetField(0x22F4, ("skillEnable", c_uint32 * 32)),  # char 1 offset abs=0xA7F4
                OffsetField(0x2374, ("slotMagicArts", c_uint32 * 8)),  # char 1 offset abs=0xA874
                OffsetField(0x2394, ("slotShortcutUser", c_uint32 * 8)),  # char 1 offset abs=0xA894
                OffsetField(0x23B4, ("slotShortcutMagicArts", c_uint32 * 8)),  # char 1 offset abs=0xA8B4
                OffsetField(0x23D4, ("condition", c_uint32)),  # char 1 offset abs=0xA8D4
                OffsetField(0x23F0, ("conditionTime", c_float * 32)),  # char 1 offset abs=0xA8F0
                OffsetField(0x2470, ("conditionEffect", c_float * 32)),  # char 1 offset abs=0xA970
                OffsetField(0x24F0, ("bTipoEquip", c_bool)),  # char 1 offset abs=0xA9F0
                OffsetField(0x24F4, ("skillRecommendedType", c_uint32)),  # char 1 offset abs=0xA9F4
                OffsetField(0x2500, ("firstName", c_char * 64)),  # char 1 offset abs=0xAA00
                OffsetField(0x2540, ("partyType", c_uint32)),  # char 1 offset abs=0xAA40
                OffsetField(0x2544, ("costume", c_uint32)),  # char 1 offset abs=0xAA44
                OffsetField(0x2548, ("hair", c_uint32)),  # char 1 offset abs=0xAA48
                OffsetField(0x254C, ("attachment", c_uint32 * 3)),  # char 1 offset abs=0xAA4C
                OffsetField(0x2560, ("attachmentMatrix", Matrix * 3)),  # char 1 offset abs=0xAA60
                OffsetField(0x2620, ("attachmentColor", Color * 3)),  # char 1 offset abs=0xAB20
                OffsetField(0x2650, ("attachmentTransform", c_uint32 * 3)),  # char 1 offset abs=0xAB50
                OffsetField(0x265C, ("totalExp", c_uint32)),  # char 1 offset abs=0xAB5C
                OffsetField(0x2660, ("gp", c_uint32)),  # char 1 offset abs=0xAB60
                OffsetField(0x2664, ("formationIndex", Vector2i)),  # char 1 offset abs=0xAB64
                OffsetField(0x266C, ("baseResidueHPMax", c_float)),  # char 1 offset abs=0xAB6C
                OffsetField(0x2670, ("baseResidueTPMax", c_float)),  # char 1 offset abs=0xAB70
                OffsetField(0x2674, ("baseResidueACMax", c_float)),  # char 1 offset abs=0xAB74
                OffsetField(0x2678, ("baseResidueSPMax", c_float)),  # char 1 offset abs=0xAB78
                OffsetField(0x267C, ("baseResidueStrength", c_float)),  # char 1 offset abs=0xAB7C
                OffsetField(0x2680, ("baseResidueIntelligence", c_float)),  # char 1 offset abs=0xAB80
                OffsetField(0x2684, ("baseResidueStamina", c_float)),  # char 1 offset abs=0xAB84
                OffsetField(0x2688, ("baseResidueDexterity", c_float)),  # char 1 offset abs=0xAB88
                OffsetField(0x268C, ("baseResidueAgility", c_float)),  # char 1 offset abs=0xAB8C
                OffsetField(0x2690, ("baseResidueSpirit", c_float)),  # char 1 offset abs=0xAB90
                OffsetField(0x2694, ("baseResidueLuck", c_float)),  # char 1 offset abs=0xAB94
                OffsetField(0x2698, ("counter", c_uint32 * 16)),  # char 1 offset abs=0xAB98
                OffsetField(0x26D8, ("strategy", c_uint32 * 7)),  # char 1 offset abs=0xABD8
                OffsetField(0x26F4, ("equipmentStack", c_uint32 * 4)),  # char 1 offset abs=0xABF4
                OffsetField(0x2704, ("costumeStack", c_uint32)),  # char 1 offset abs=0xAC04
                OffsetField(0x2708, ("hairStack", c_uint32)),  # char 1 offset abs=0xAC08
                OffsetField(0x270C, ("attachmentStack", c_uint32 * 3)),  # char 1 offset abs=0xAC0C
                OffsetField(0x2718, ("baseCoefficientHPMax", c_uint32)),  # char 1 offset abs=0xAC18
                OffsetField(0x271C, ("baseCoefficientTPMax", c_uint32)),  # char 1 offset abs=0xAC1C
                OffsetField(0x2720, ("baseCoefficientACMax", c_uint32)),  # char 1 offset abs=0xAC20
                OffsetField(0x2724, ("baseCoefficientSPMax", c_uint32)),  # char 1 offset abs=0xAC24
                OffsetField(0x2728, ("baseCoefficientStrength", c_uint32)),  # char 1 offset abs=0xAC28
                OffsetField(0x272C, ("baseCoefficientIntelligence", c_uint32)),  # char 1 offset abs=0xAC2C
                OffsetField(0x2730, ("baseCoefficientStamina", c_uint32)),  # char 1 offset abs=0xAC30
                OffsetField(0x2734, ("baseCoefficientDexterity", c_uint32)),  # char 1 offset abs=0xAC34
                OffsetField(0x2738, ("baseCoefficientAgility", c_uint32)),  # char 1 offset abs=0xAC38
                OffsetField(0x273C, ("baseCoefficientSpirit", c_uint32)),  # char 1 offset abs=0xAC3C
                OffsetField(0x2740, ("baseCoefficientLuck", c_uint32)),  # char 1 offset abs=0xAC40
                OffsetField(0x2744, ("herbHPMax", c_uint32)),  # char 1 offset abs=0xAC44
                OffsetField(0x2748, ("herbTPMax", c_uint32)),  # char 1 offset abs=0xAC48
                OffsetField(0x274C, ("herbSPMax", c_uint32)),  # char 1 offset abs=0xAC4C
                OffsetField(0x2750, ("herbStrength", c_uint32)),  # char 1 offset abs=0xAC50
                OffsetField(0x2754, ("herbIntelligence", c_uint32)),  # char 1 offset abs=0xAC54
                OffsetField(0x2758, ("herbStamina", c_uint32)),  # char 1 offset abs=0xAC58
                OffsetField(0x275C, ("herbDexterity", c_uint32)),  # char 1 offset abs=0xAC5C
                OffsetField(0x2760, ("herbAgility", c_uint32)),  # char 1 offset abs=0xAC60
                OffsetField(0x2764, ("herbSpirit", c_uint32)),  # char 1 offset abs=0xAC64
            ]

        # Assert specific field offsets to help with debugging
        assert_field_offset(PlayerStatus, "attachmentColor", 0xAB20 - 0x8500)
        assert_field_offset(PlayerStatus, "herbSpirit", 0xAC64 - 0x8500)

        _size_ = 0x2778
        _offset_fields_ = [
            OffsetField(0x0, ("mVersion", c_uint32)),  # char 1 offset abs=0x84F0
            OffsetField(0x10, ("mStatus", PlayerStatus)),  # char 1 offset rel=0x10, abs=0x8500
        ]

    class LinkInfo(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x28
        _offset_fields_ = [
            OffsetField(0x0, ("condition", c_uint32)),
            OffsetField(0x4, ("partner", c_uint32)),
            OffsetField(0x8, ("colorPattern", c_uint32)),
            OffsetField(0xC, ("frame", c_uint32)),
            OffsetField(0x10, ("history", c_uint32 * 6)),
        ]

    class GrowthStatus(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x19C
        _offset_fields_ = [
            OffsetField(0x0, ("mNodeFlag", c_uint8 * 128)),  # char 1 offset abs=0xE8F0
            OffsetField(0x80, ("mLineFlag", c_uint8 * 128)),  # char 1 offset abs=0xE970
            OffsetField(0x100, ("mPlaneFlag", c_uint8 * 64)),  # char 1 offset abs=0xE9F0
            OffsetField(0x140, ("mOrbLevel", c_uint32 * 4)),  # char 1 offset abs=0xEA30
            OffsetField(0x150, ("mNodeNumFlag", c_uint32 * 4)),  # char 1 offset abs=0xEA40
            OffsetField(0x160, ("mLineNumFlag", c_uint32 * 4)),  # char 1 offset abs=0xEA50
            OffsetField(0x170, ("mPlaneNumFlag", c_uint32 * 4)),  # char 1 offset abs=0xEA60
            OffsetField(0x180, ("mCurrentOrbSheet", c_uint32)),  # char 1 offset abs=0xEA70
            OffsetField(0x184, ("mCurrentNode", c_uint32 * 4)),  # char 1 offset abs=0xEA74
            OffsetField(0x194, ("mNumOrbSheet", c_uint32)),  # char 1 offset abs=0xEA84
            OffsetField(0x198, ("mNumEnableMaxOrbSheet", c_uint32)),  #  char 1 offset abs=0xEA88
        ]

    class AttachmentCustomData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x120
        _offset_fields_ = [
            OffsetField(0x0, ("mCostume", c_uint32)),  # char 1 offset rel=0x0, abs=0xECF0
            OffsetField(0x4, ("mHair", c_uint32)),  # char 1 offset rel=0x4, abs=0xECF4
            OffsetField(0x8, ("mAttachment", c_uint32 * 3)),  # char 1 offset rel=0x8, abs=0xECF8
            OffsetField(0x20, ("mAttachmentMatrix", Matrix * 3)),  # char 1 offset rel=0x20, abs=0xED10
            OffsetField(0xE0, ("mAttachmentColor", Color * 3)),  # char 1 offset rel=0xE0, abs=0xEDD0
            OffsetField(0x110, ("mAttachmentTransform", c_uint32 * 3)),  # char 1 offset rel=0x110, abs=0xEE00
        ]

    class GrowthTransferData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x240
        _offset_fields_ = [
            OffsetField(0x0, ("mNodeGettingOrder", c_uint16 * 288)),
        ]

    _size_ = 0xA000
    _offset_fields_ = [
        OffsetField(0x0, ("mPlayerStatusData", PlayerStatusData)),  # char 1 offset abs=0x84F0
        OffsetField(0x6000, ("mLinkInfo", LinkInfo)),  # char 1 offset rel=0x6000, abs=0xE4F0
        OffsetField(0x6400, ("mGrowthStatus", GrowthStatus)),  # char 1 offset rel=0x6400, abs=0xE8F0
        OffsetField(
            0x6800,
            ("mAttachmentCustomData", AttachmentCustomData * 8),  #  type: ignore[arg-type,operator]
        ),  # char 1 offset rel=0x6800, abs=0xECF0
        OffsetField(0x7400, ("mGrowthTransferData", GrowthTransferData)),  # char 1 offset rel=0x7400, abs=0xF8F0
        # The "mGrowthTransferReferenceData" appears to not be used in PS3 save
        # So just copy over the "mGrowthTransferData: field when converting to PC
    ]

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Override to the set the mGrowthTransferReferenceData field to mGrowthTransferData
        Also sets the formation index field to a float
        """
        # Initialize a default player status save data dict with all the required
        # fields and then merge the marshaled results into it
        output_dict: PlayerStatusSaveDataDict = create_player1_status_save_dict()
        dict_result = super().to_dict(skip_double_underscore_fields)

        if not dict_result or not dict_result.value:
            return dict_result

        output_dict |= cast(PlayerStatusSaveDataDict, cast(object, dict_result.value))
        # Set the 'mGrowthTransferReferenceData' field to `mGrowthTransferData`
        # as the PS3 save does not contain that data
        output_dict["mGrowthTransferReferenceData"] = output_dict["mGrowthTransferData"]

        output_dict["mPlayerStatusData"]["mStatus"]["formationIndex"]["x"] = float(
            output_dict["mPlayerStatusData"]["mStatus"]["formationIndex"]["x"]
        )
        output_dict["mPlayerStatusData"]["mStatus"]["formationIndex"]["y"] = float(
            output_dict["mPlayerStatusData"]["mStatus"]["formationIndex"]["y"]
        )

        return ToDictResult(True, output_dict)


assert_struct_no_padding(PLAYER_STATUS_SAVE_DATA)
