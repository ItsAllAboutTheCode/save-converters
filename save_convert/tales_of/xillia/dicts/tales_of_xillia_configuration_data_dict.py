"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class ConfigurationData(TypedDict):
    mVersion: int
    mMessageSpeed: int
    mBattleRank: int
    mBattleEncount: int
    mBattleDynamicCamera: int
    mBattleEncountCamera: int
    mMapCameraSpeed: int
    mMapCameraYaw: int
    mMapCameraPitch: int
    mMapCameraAutoAdjust: int
    mSoundOutput: int
    mVolumeAll: int
    mVolumeBGM: int
    mVolumeSE: int
    mVolumeVoice: int
    mVolumeMovie: int
    mVibration: int
    mBrightness: int
    mAutoMessage: int
    mExtendInputAhead: int
    mNavigationMapRotateFixed: int
    mCaption: int
    mBattleCameraOffsetElevation: int
    mBattleCameraOffsetDistance: int
    mMapCameraDistance: int
    mMiniMap: int
    mLocationMap: int
    mVoiceLanguage: int
    mEventSkip: int
    mBtlCaption: int
    mBtlBGM: int
    mBtlBGMDataID: list[int]
    mEventPointView: int


class SaveDataIDConfigurationDataSaveDict(TypedDict):
    mConfigurationData: ConfigurationData


def create_save_data_id_configuration_save_dict() -> SaveDataIDConfigurationDataSaveDict:
    return {
        "mConfigurationData": {
            "mVersion": 100,
            "mMessageSpeed": 0,
            "mBattleRank": 0,
            "mBattleEncount": 1,
            "mBattleDynamicCamera": 1,
            "mBattleEncountCamera": 1,
            "mMapCameraSpeed": 5,
            "mMapCameraYaw": 0,
            "mMapCameraPitch": 0,
            "mMapCameraAutoAdjust": 1,
            "mSoundOutput": 0,
            "mVolumeAll": 8,
            "mVolumeBGM": 8,
            "mVolumeSE": 8,
            "mVolumeVoice": 8,
            "mVolumeMovie": 8,
            "mVibration": 1,
            "mBrightness": 0,
            "mAutoMessage": 1,
            "mExtendInputAhead": 0,
            "mNavigationMapRotateFixed": 0,
            "mCaption": 1,
            "mBattleCameraOffsetElevation": 0,
            "mBattleCameraOffsetDistance": 0,
            "mMapCameraDistance": 1,
            "mMiniMap": 1,
            "mLocationMap": 1,
            "mVoiceLanguage": 1,
            "mEventSkip": 0,
            "mBtlCaption": 1,
            "mBtlBGM": 0,
            "mBtlBGMDataID": [],
            "mEventPointView": 1,
        }
    }
