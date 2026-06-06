"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32
from typing import override

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    ToDictResult,
    assert_struct_size,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_configuration_data_dict import (
    SaveDataIDConfigurationDataSaveDict,
    create_save_data_id_configuration_save_dict,
)


class SAVE_DATA_ID_CONFIGURATION_DATA(MarshalStructure):
    class ConfigurationData(MarshalStructure):
        _fields_ = [
            ("mVersion", c_uint32),  # offset abs=0x699D0
            ("mMessageSpeed", c_uint32),  # offset abs=0x699D4
            ("mBattleRank", c_uint32),  # offset abs=0x699D8
            # ("mBattleEncount", c_uint32),
            ("mBattleDynamicCamera", c_uint32),  # offset abs=0x699DC
            ("mBattleEncountCamera", c_uint32),  # offset abs=0x699E0
            ("mMapCameraSpeed", c_uint32),  # offset abs=0x699E4
            ("mMapCameraYaw", c_uint32),  # offset abs=0x699E8
            ("mMapCameraPitch", c_uint32),  # offset abs=0x699EC
            ("mMapCameraAutoAdjust", c_uint32),  # offset abs=0x699F0
            ("mSoundOutput", c_uint32),  # offset abs=0x699F4
            # ("mVolumeAll", c_uint32),
            ("mVolumeBGM", c_uint32),  # offset abs=0x699F8
            ("mVolumeSE", c_uint32),  # offset abs=0x699FC
            ("mVolumeVoice", c_uint32),  # offset abs=0x69A00
            ("mVolumeMovie", c_uint32),  # offset abs=0x69A04
            ("mVibration", c_uint32),  # offset abs=0x69A08
            # ("mBrightness", c_uint32),
            ("__unknown_ps3_setting1__", c_uint32),  # offset abs=0x69A0C
            ("__unknown_ps3_setting2__", c_uint32),  # offset abs=0x69A10
            ("__unknown_ps3_setting3__", c_uint32),  # offset abs=0x69A14
            ("__unknown_ps3_setting4__", c_uint32),  # offset abs=0x69A18
            ("mAutoMessage", c_uint32),  # offset abs=0x69A1C
            ("mExtendInputAhead", c_uint32),  # offset abs=0x69A20
            ("mNavigationMapRotateFixed", c_uint32),  # offset abs=0x69A24
            ("mCaption", c_uint32),  # offset 0x69A28
            ("__unknown_ps3_setting5__", c_uint32),  # offset abs=0x69A2C
            ("__unknown_ps3_setting6__", c_uint32),  # offset abs=0x69A30
            ("__align_to_4094__", c_uint32 * (1024 - 25)),  # Appears to be 24 settings + 4 byte version in PS3 save
            # The below appears to be remaster only settings
            # ("mBattleCameraOffsetElevation", c_uint32),
            # ("mBattleCameraOffsetDistance", c_uint32),
            # ("mMapCameraDistance", c_uint32),
            # ("mMiniMap", c_uint32),
            # ("mLocationMap", c_uint32),
            # ("mVoiceLanguage", c_uint32),
            # ("mEventSkip", c_uint32),
            # ("mBtlCaption", c_uint32),
            # ("mBtlBGM", c_uint32),
            # ("mBtlBGMDataID", c_uint8 * 8),
            # ("mEventPointView", c_uint32),
        ]

    _fields_ = [
        ("mConfigurationData", ConfigurationData),
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


assert_struct_size(SAVE_DATA_ID_CONFIGURATION_DATA, 0x1000)
