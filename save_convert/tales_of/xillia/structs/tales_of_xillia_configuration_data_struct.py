"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32
from typing import override

from save_convert.structs.marshal_dict_base import ToDictResult
from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField
from save_convert.tales_of.xillia.dicts.tales_of_xillia_configuration_data_dict import (
    SaveDataIDConfigurationDataSaveDict,
    create_save_data_id_configuration_save_dict,
)


class SAVE_DATA_ID_CONFIGURATION_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class ConfigurationData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x1000
        _offset_fields_ = [
            OffsetField(0x0, ("mVersion", c_uint32)),  # offset abs=0x699D0
            OffsetField(0x4, ("mMessageSpeed", c_uint32)),  # offset abs=0x699D4
            OffsetField(0x8, ("mBattleRank", c_uint32)),  # offset abs=0x699D8
            OffsetField(0xC, ("mBattleDynamicCamera", c_uint32)),  # offset abs=0x699DC
            OffsetField(0x10, ("mBattleEncountCamera", c_uint32)),  # offset abs=0x699E0
            OffsetField(0x14, ("mMapCameraSpeed", c_uint32)),  # offset abs=0x699E4
            OffsetField(0x18, ("mMapCameraYaw", c_uint32)),  # offset abs=0x699E8
            OffsetField(0x1C, ("mMapCameraPitch", c_uint32)),  # offset abs=0x699EC
            OffsetField(0x20, ("mMapCameraAutoAdjust", c_uint32)),  # offset abs=0x699F0
            OffsetField(0x24, ("mSoundOutput", c_uint32)),  # offset abs=0x699F4
            OffsetField(0x28, ("mVolumeBGM", c_uint32)),  # offset abs=0x699F8
            OffsetField(0x2C, ("mVolumeSE", c_uint32)),  # offset abs=0x699FC
            OffsetField(0x30, ("mVolumeVoice", c_uint32)),  # offset abs=0x69A00
            OffsetField(0x34, ("mVolumeMovie", c_uint32)),  # offset abs=0x69A04
            OffsetField(0x38, ("mVibration", c_uint32)),  # offset abs=0x69A08
            OffsetField(0x4C, ("mAutoMessage", c_uint32)),  # offset abs=0x69A1C
            OffsetField(0x50, ("mExtendInputAhead", c_uint32)),  # offset abs=0x69A20
            OffsetField(0x54, ("mNavigationMapRotateFixed", c_uint32)),  # offset abs=0x69A24
            OffsetField(0x58, ("mCaption", c_uint32)),  # offset 0x69A28
            # The below appears to be remaster only settings
            # ("mBattleEncount", c_uint32)),
            # ("mVolumeAll", c_uint32)),
            # ("mBrightness", c_uint32)),
            # ("mBattleCameraOffsetElevation", c_uint32)),
            # ("mBattleCameraOffsetDistance", c_uint32)),
            # ("mMapCameraDistance", c_uint32)),
            # ("mMiniMap", c_uint32)),
            # ("mLocationMap", c_uint32)),
            # ("mVoiceLanguage", c_uint32)),
            # ("mEventSkip", c_uint32)),
            # ("mBtlCaption", c_uint32)),
            # ("mBtlBGM", c_uint32)),
            # ("mBtlBGMDataID", c_uint8 * 8)),
            # ("mEventPointView", c_uint32)),
        ]

    _size_ = 0x1000
    _offset_fields_ = [
        OffsetField(0x0, ("mConfigurationData", ConfigurationData)),
    ]

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Override which adds the missing Xillia remaster only settings to the Configuration Data JSON
        """

        output_dict: SaveDataIDConfigurationDataSaveDict = create_save_data_id_configuration_save_dict()
        dict_result = super().to_dict(skip_double_underscore_fields)

        if not dict_result or not dict_result.value:
            return dict_result

        output_dict["mConfigurationData"] |= dict_result.value.get("mConfigurationData", {})

        return ToDictResult(True, output_dict)


assert_struct_no_padding(SAVE_DATA_ID_CONFIGURATION_DATA)
