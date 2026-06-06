"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_char, c_float, c_uint8, c_uint16, c_uint32
from typing import cast, override

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    ToDictResult,
    assert_field_offset,
    assert_struct_size,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_player_status_dict import (
    PlayerStatusSaveDataDict,
    create_player1_status_save_dict,
)
from save_convert.tales_of.xillia.structs.tales_of_xillia_math_structs import Color, Matrix, Vector2i


class PLAYER_STATUS_SAVE_DATA(MarshalStructure):
    """
    Note the PS3 save stores the "formationIndex: field as two uint32_t objects
    while the Remaster save stores it as 2 floats
    """

    class PlayerStatusData(MarshalStructure):
        class PlayerStatus(MarshalStructure):
            _fields_ = [
                ("bParty", c_bool),  # char 1 offset abs=0x8500
                ("__padding1__", c_uint8 * 3),
                ("partyID", c_uint32),  # char 1 offset abs=0x8504
                ("level", c_uint32),  # char 1 offset abs=0x8508
                ("hp", c_uint32),  # char 1 offset abs=0x850C
                ("tp", c_uint32),  # char 1 offset abs=0x8510
                ("ac", c_uint32),  # char 1 offset abs=0x8514
                ("__padding2__", c_uint8 * 8),  # char 1 offset abs=0x8518
                ("baseHPMax", c_uint32),  # char 1 offset abs=0x8520
                ("baseTPMax", c_uint32),  # char 1 offset abs=0x8524
                ("baseACMax", c_uint32),  # char 1 offset abs=0x8528
                ("baseSPMax", c_uint32),  # char 1 offset abs=0x852C
                ("baseStrength", c_uint32),  # char 1 offset abs=0x8530
                ("baseIntelligence", c_uint32),  # char 1 offset abs=0x8534
                ("baseStamina", c_uint32),  # char 1 offset abs=0x8538
                ("baseDexterity", c_uint32),  # char 1 offset abs=0x853C
                ("baseAgility", c_uint32),  # char 1 offset abs=0x8540
                ("baseSpirit", c_uint32),  # char 1 offset abs=0x8544
                ("baseLuck", c_uint32),  # char 1 offset abs=0x8548
                ("elementEndurance", c_float * 6),  # char 1 offset abs=0x854C
                ("equipment", c_uint32 * 4),  # char 1 offset abs=0x8564
                ("magicArtsLearn", c_uint32 * 64),  # char 1 offset abs=0x8574
                ("magicArtsEnable", c_uint32 * 64),  # char 1 offset abs=0x8674
                ("magicArtsCount", c_uint32 * 2048),  # char 1 offset abs=0x8774
                ("skillLearn", c_uint32 * 32),  # char 1 offset abs=0xA774
                ("skillEnable", c_uint32 * 32),  # char 1 offset abs=0xA7F4
                ("slotMagicArts", c_uint32 * 8),  # char 1 offset abs=0xA874
                ("slotShortcutUser", c_uint32 * 8),  # char 1 offset abs=0xA894
                ("slotShortcutMagicArts", c_uint32 * 8),  # char 1 offset abs=0xA8B4
                ("condition", c_uint32),  # char 1 offset abs=0xA8D4
                ("__padding3__", c_uint8 * 24),  # char 1 offset abs=0xA8D8
                ("conditionTime", c_float * 32),  # char 1 offset abs=0xA8F0
                ("conditionEffect", c_float * 32),  # char 1 offset abs=0xA970
                ("bTipoEquip", c_bool),  # char 1 offset abs=0xA9F0
                ("__padding4__", c_uint8 * 3),  # char 1 offset abs=0xA9F1
                ("skillRecommendedType", c_uint32),  # char 1 offset abs=0xA9F4
                ("__padding5__", c_uint8 * 8),  # char 1 offset abs=0xA9F8
                ("firstName", c_char * 64),  # char 1 offset abs=0xAA00
                ("partyType", c_uint32),  # char 1 offset abs=0xAA40
                ("costume", c_uint32),  # char 1 offset abs=0xAA44
                ("hair", c_uint32),  # char 1 offset abs=0xAA48
                ("attachment", c_uint32 * 3),  # char 1 offset abs=0xAA4C
                ("__padding6__", c_uint8 * 8),  # char 1 offset abs=0xAA58
                ("attachmentMatrix", Matrix * 3),  # char 1 offset abs=0xAA60
                ("attachmentColor", Color * 3),  # char 1 offset abs=0xAB20
                ("attachmentTransform", c_uint32 * 3),  # char 1 offset abs=0xAB50
                ("totalExp", c_uint32),  # char 1 offset abs=0xAB5C
                ("gp", c_uint32),  # char 1 offset abs=0xAB60
                ("formationIndex", Vector2i),  # char 1 offset abs=0xAB64
                ("baseResidueHPMax", c_float),  # char 1 offset abs=0xAB6C
                ("baseResidueTPMax", c_float),  # char 1 offset abs=0xAB70
                ("baseResidueACMax", c_float),  # char 1 offset abs=0xAB74
                ("baseResidueSPMax", c_float),  # char 1 offset abs=0xAB78
                ("baseResidueStrength", c_float),  # char 1 offset abs=0xAB7C
                ("baseResidueIntelligence", c_float),  # char 1 offset abs=0xAB80
                ("baseResidueStamina", c_float),  # char 1 offset abs=0xAB84
                ("baseResidueDexterity", c_float),  # char 1 offset abs=0xAB88
                ("baseResidueAgility", c_float),  # char 1 offset abs=0xAB8C
                ("baseResidueSpirit", c_float),  # char 1 offset abs=0xAB90
                ("baseResidueLuck", c_float),  # char 1 offset abs=0xAB94
                ("counter", c_uint32 * 16),  # char 1 offset abs=0xAB98
                ("strategy", c_uint32 * 7),  # char 1 offset abs=0xABD8
                ("equipmentStack", c_uint32 * 4),  # char 1 offset abs=0xABF4
                ("costumeStack", c_uint32),  # char 1 offset abs=0xAC04
                ("hairStack", c_uint32),  # char 1 offset abs=0xAC08
                ("attachmentStack", c_uint32 * 3),  # char 1 offset abs=0xAC14
                ("baseCoefficientHPMax", c_uint32),  # char 1 offset abs=0xAC18
                ("baseCoefficientTPMax", c_uint32),  # char 1 offset abs=0xAC1C
                ("baseCoefficientACMax", c_uint32),  # char 1 offset abs=0xAC20
                ("baseCoefficientSPMax", c_uint32),  # char 1 offset abs=0xAC24
                ("baseCoefficientStrength", c_uint32),  # char 1 offset abs=0xAC28
                ("baseCoefficientIntelligence", c_uint32),  # char 1 offset abs=0xAC2C
                ("baseCoefficientStamina", c_uint32),  # char 1 offset abs=0xAC30
                ("baseCoefficientDexterity", c_uint32),  # char 1 offset abs=0xAC34
                ("baseCoefficientAgility", c_uint32),  # char 1 offset abs=0xAC38
                ("baseCoefficientSpirit", c_uint32),  # char 1 offset abs=0xAC3C
                ("baseCoefficientLuck", c_uint32),  # char 1 offset abs=0xAC40
                ("herbHPMax", c_uint32),  # char 1 offset abs=0xAC44
                ("herbTPMax", c_uint32),  # char 1 offset abs=0xAC48
                ("herbSPMax", c_uint32),  # char 1 offset abs=0xAC4C
                ("herbStrength", c_uint32),  # char 1 offset abs=0xAC50
                ("herbIntelligence", c_uint32),  # char 1 offset abs=0xAC54
                ("herbStamina", c_uint32),  # char 1 offset abs=0xAC58
                ("herbDexterity", c_uint32),  # char 1 offset abs=0xAC5C
                ("herbAgility", c_uint32),  # char 1 offset abs=0xAC60
                ("herbSpirit", c_uint32),  # char 1 offset abs=0xAC64
            ]

        # Assert specific field offsets to help with debugging
        assert_field_offset(PlayerStatus, "attachmentColor", 0xAB20 - 0x8500)
        assert_field_offset(PlayerStatus, "herbSpirit", 0xAC64 - 0x8500)

        _fields_ = [
            ("mVersion", c_uint32),  # char 1 offset abs=0x84F0
            ("__align__to_16__", c_uint8 * 12),
            ("mStatus", PlayerStatus),  # char 1 offset rel=0x10, abs=0x8500
        ]

    class LinkInfo(MarshalStructure):
        _fields_ = [
            ("condition", c_uint32),
            ("partner", c_uint32),
            ("colorPattern", c_uint32),
            ("frame", c_uint32),
            ("history", c_uint32 * 6),
        ]

    class GrowthStatus(MarshalStructure):
        _fields_ = [
            ("mNodeFlag", c_uint8 * 128),  # char 1 offset abs=0xE8F0
            ("mLineFlag", c_uint8 * 128),  # char 1 offset abs=0xE970
            ("mPlaneFlag", c_uint8 * 64),  # char 1 offset abs=0xE9F0
            ("mOrbLevel", c_uint32 * 4),  # char 1 offset abs=0xEA30
            ("mNodeNumFlag", c_uint32 * 4),  # char 1 offset abs=0xEA40
            ("mLineNumFlag", c_uint32 * 4),  # char 1 offset abs=0xEA50
            ("mPlaneNumFlag", c_uint32 * 4),  # char 1 offset abs=0xEA60
            ("mCurrentOrbSheet", c_uint32),  # char 1 offset abs=0xEA70
            ("mCurrentNode", c_uint32 * 4),  # char 1 offset abs=0xEA74
            ("mNumOrbSheet", c_uint32),  # char 1 offset abs=0xEA84
            ("mNumEnableMaxOrbSheet", c_uint32),  #  char 1 offset abs=0xEA88
        ]

    class AttachmentCustomData(MarshalStructure):
        _fields_ = [
            ("mCostume", c_uint32),  # char 1 offset abs=0xECF0
            ("mHair", c_uint32),  # char 1 offset abs=0xECF4
            ("mAttachment", c_uint32 * 3),  # char 1 offset abs=0xECF8
            ("__align_matrix_to_16__", c_uint32 * 3),  # char 1 offset abs=0xED04
            ("mAttachmentMatrix", Matrix * 3),  # char 1 offset abs=0xED10
            ("mAttachmentColor", Color * 3),  # char 1 offset abs=0xEDD0
            ("mAttachmentTransform", c_uint32 * 3),
            ("__align_to_struct_to_16", c_uint32),
        ]

    class GrowthTransferData(MarshalStructure):
        _fields_ = [
            ("mNodeGettingOrder", c_uint16 * 288),
        ]

    assert_struct_size(PlayerStatusData, 0x2778)
    assert_struct_size(LinkInfo, 0x28)
    assert_struct_size(GrowthStatus, 0x19C)
    assert_struct_size(AttachmentCustomData, 0x120)
    assert_struct_size(GrowthTransferData, 0x240)

    _fields_ = [
        ("mPlayerStatusData", PlayerStatusData),  # char 1 offset abs=0x84F0
        ("__align_to_link_info__", c_uint8 * (0x6000 - 0x2778)),
        ("mLinkInfo", LinkInfo),  # char 1 offset rel=0x6000, abs=0xE4F0
        ("__align_to_growth_status__", c_uint8 * (0x400 - 0x28)),
        ("mGrowthStatus", GrowthStatus),  # char 1 offset rel=0x6400, abs=0xE8F0
        ("__align_to_attachment_custom_data__", c_uint8 * (0x400 - 0x19C)),
        ("mAttachmentCustomData", AttachmentCustomData * 8),  # char 1 offset rel=0x6800, abs=0xECF0
        ("__align_to_growth_transfer__", c_uint8 * (0xC00 - 0x900)),
        ("mGrowthTransferData", GrowthTransferData),  # char 1 offset rel=0x7400, abs=0xF8F0
        # The "mGrowthTransferReferenceData" appears to not be used in PS3 save
        # So just copy over the "mGrowthTransferData: field when converting to PC
        # ("mGrowthTransferReferenceData", GrowthTransferData),  # char 1 offset abs=0xFA10
        ("__align__to_40960__", c_uint8 * (0xA000 - 0x7640)),  # char 1 offset rel=0x7640, abs=0xFB30
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


assert_field_offset(PLAYER_STATUS_SAVE_DATA, "mLinkInfo", 0x6000)
assert_field_offset(PLAYER_STATUS_SAVE_DATA, "__align__to_40960__", 0x7640)
assert_struct_size(PLAYER_STATUS_SAVE_DATA, 0xA000)
