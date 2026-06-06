"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict

from save_convert.tales_of.xillia.dicts.tales_of_xillia_math_dicts import Color, Matrix, Vector2


class PlayerStatus(TypedDict):
    bParty: bool
    partyID: int
    level: int
    hp: int
    tp: int
    ac: int
    baseHPMax: int
    baseTPMax: int
    baseACMax: int
    baseSPMax: int
    baseStrength: int
    baseIntelligence: int
    baseStamina: int
    baseDexterity: int
    baseAgility: int
    baseSpirit: int
    baseLuck: int
    elementEndurance: list[float]
    equipment: list[int]
    magicArtsLearn: list[int]
    magicArtsEnable: list[int]
    magicArtsCount: list[int]
    skillLearn: list[int]
    skillEnable: list[int]
    slotMagicArts: list[int]
    slotShortcutUser: list[int]
    slotShortcutMagicArts: list[int]
    condition: int
    conditionTime: list[float]
    conditionEffect: list[float]
    bTipoEquip: bool
    skillRecommendedType: int
    firstName: str
    partyType: int
    costume: int
    hair: int
    attachment: list[int]
    attachmentMatrix: list[Matrix]
    attachmentColor: list[Color]
    attachmentTransform: list[int]
    totalExp: int
    gp: int
    formationIndex: Vector2
    baseResidueHPMax: float
    baseResidueTPMax: float
    baseResidueACMax: float
    baseResidueSPMax: float
    baseResidueStrength: float
    baseResidueIntelligence: float
    baseResidueStamina: float
    baseResidueDexterity: float
    baseResidueAgility: float
    baseResidueSpirit: float
    baseResidueLuck: float
    counter: list[int]
    strategy: list[int]
    equipmentStack: list[int]
    costumeStack: int
    hairStack: int
    attachmentStack: list[int]
    baseCoefficientHPMax: int
    baseCoefficientTPMax: int
    baseCoefficientACMax: int
    baseCoefficientSPMax: int
    baseCoefficientStrength: int
    baseCoefficientIntelligence: int
    baseCoefficientStamina: int
    baseCoefficientDexterity: int
    baseCoefficientAgility: int
    baseCoefficientSpirit: int
    baseCoefficientLuck: int
    herbHPMax: int
    herbTPMax: int
    herbSPMax: int
    herbStrength: int
    herbIntelligence: int
    herbStamina: int
    herbDexterity: int
    herbAgility: int
    herbSpirit: int


class PlayerStatusData(TypedDict):
    mVersion: int
    mStatus: PlayerStatus


class LinkInfo(TypedDict):
    condition: int
    partner: int
    colorPattern: int
    frame: int
    history: list[int]


class GrowthStatus(TypedDict):
    mNodeFlag: list[int]
    mLineFlag: list[int]
    mPlaneFlag: list[int]
    mOrbLevel: list[int]
    mNodeNumFlag: list[int]
    mLineNumFlag: list[int]
    mPlaneNumFlag: list[int]
    mCurrentOrbSheet: int
    mCurrentNode: list[int]
    mNumOrbSheet: int
    mNumEnableMaxOrbSheet: int


class AttachmentCustomData(TypedDict):
    mCostume: int
    mHair: int
    mAttachment: list[int]
    mAttachmentMatrix: list[Matrix]
    mAttachmentColor: list[Color]
    mAttachmentTransform: list[int]


class GrowthTransferData(TypedDict):
    mNodeGettingOrder: list[int]


class PlayerStatusSaveDataDict(TypedDict):
    mPlayerStatusData: PlayerStatusData
    mLinkInfo: LinkInfo
    mGrowthStatus: GrowthStatus
    mAttachmentCustomData: list[AttachmentCustomData]
    mGrowthTransferData: GrowthTransferData
    mGrowthTransferReferenceData: GrowthTransferData


def create_player1_status_save_dict() -> PlayerStatusSaveDataDict:
    return {
        "mPlayerStatusData": {
            "mVersion": 103,
            "mStatus": {
                "bParty": True,
                "partyID": 1,
                "level": 1,
                "hp": 430,
                "tp": 100,
                "ac": 0,
                "baseHPMax": 430,
                "baseTPMax": 100,
                "baseACMax": 4,
                "baseSPMax": 10,
                "baseStrength": 54,
                "baseIntelligence": 37,
                "baseStamina": 42,
                "baseDexterity": 43,
                "baseAgility": 60,
                "baseSpirit": 44,
                "baseLuck": 76,
                "elementEndurance": [100.0] * 6,
                "equipment": [0, 0, 0, 0],
                "magicArtsLearn": [40960] + [0] * 63,
                "magicArtsEnable": [4294967295] * 64,
                "magicArtsCount": [0] * 2048,
                "skillLearn": [0] * 32,
                "skillEnable": [0] * 32,
                "slotMagicArts": [13, 15] + [0] * 6,
                "slotShortcutUser": [0] * 8,
                "slotShortcutMagicArts": [0] * 8,
                "condition": 0,
                "conditionTime": [0.0] * 32,
                "conditionEffect": [0.0] * 32,
                "bTipoEquip": False,
                "skillRecommendedType": 0,
                "firstName": "Jude",
                "partyType": 0,
                "costume": 67108940,
                "hair": 67108867,
                "attachment": [0] * 3,
                "attachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "attachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "attachmentTransform": [0] * 3,
                "totalExp": 0,
                "gp": 0,
                "formationIndex": {"x": 2.0, "y": 0.0},
                "baseResidueHPMax": 0.0,
                "baseResidueTPMax": 0.0,
                "baseResidueACMax": 0.0,
                "baseResidueSPMax": 0.0,
                "baseResidueStrength": 0.0,
                "baseResidueIntelligence": 0.0,
                "baseResidueStamina": 0.0,
                "baseResidueDexterity": 0.0,
                "baseResidueAgility": 0.0,
                "baseResidueSpirit": 0.0,
                "baseResidueLuck": 0.0,
                "counter": [0] * 16,
                "strategy": [1, 9, 16, 20, 25, 29, 33],
                "equipmentStack": [0, 0, 0, 0],
                "costumeStack": 0,
                "hairStack": 0,
                "attachmentStack": [0] * 3,
                "baseCoefficientHPMax": 0,
                "baseCoefficientTPMax": 0,
                "baseCoefficientACMax": 0,
                "baseCoefficientSPMax": 0,
                "baseCoefficientStrength": 0,
                "baseCoefficientIntelligence": 0,
                "baseCoefficientStamina": 0,
                "baseCoefficientDexterity": 0,
                "baseCoefficientAgility": 0,
                "baseCoefficientSpirit": 0,
                "baseCoefficientLuck": 0,
                "herbHPMax": 0,
                "herbTPMax": 0,
                "herbSPMax": 0,
                "herbStrength": 0,
                "herbIntelligence": 0,
                "herbStamina": 0,
                "herbDexterity": 0,
                "herbAgility": 0,
                "herbSpirit": 0,
            },
        },
        "mLinkInfo": {"condition": 0, "partner": 0, "colorPattern": 0, "frame": 0, "history": [0] * 6},
        "mGrowthStatus": {
            "mNodeFlag": [0] * 128,
            "mLineFlag": [0] * 128,
            "mPlaneFlag": [0] * 64,
            "mOrbLevel": [4] * 4,
            "mNodeNumFlag": [0] * 4,
            "mLineNumFlag": [0] * 4,
            "mPlaneNumFlag": [0] * 4,
            "mCurrentOrbSheet": 0,
            "mCurrentNode": [0] * 4,
            "mNumOrbSheet": 1,
            "mNumEnableMaxOrbSheet": 2,
        },
        "mAttachmentCustomData": [
            {
                "mCostume": 67108940,
                "mHair": 67108867,
                "mAttachment": [0] * 3,
                "mAttachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "mAttachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "mAttachmentTransform": [0] * 3,
            }
        ]
        * 8,
        "mGrowthTransferData": {"mNodeGettingOrder": []},
        "mGrowthTransferReferenceData": {"mNodeGettingOrder": []},
    }


def create_player2_status_save_dict() -> PlayerStatusSaveDataDict:
    return {
        "mPlayerStatusData": {
            "mVersion": 103,
            "mStatus": {
                "bParty": True,
                "partyID": 2,
                "level": 1,
                "hp": 1942,
                "tp": 262,
                "ac": 0,
                "baseHPMax": 1850,
                "baseTPMax": 250,
                "baseACMax": 4,
                "baseSPMax": 100,
                "baseStrength": 415,
                "baseIntelligence": 432,
                "baseStamina": 349,
                "baseDexterity": 374,
                "baseAgility": 410,
                "baseSpirit": 340,
                "baseLuck": 3,
                "elementEndurance": [100.0] * 6,
                "equipment": [16777240, 33554454, 33554557, 0],
                "magicArtsLearn": [0] + [2407596032] + [0] * 62,
                "magicArtsEnable": [4294967295] * 64,
                "magicArtsCount": [0] * 2048,
                "skillLearn": [
                    575218834,
                    268435456,
                    536870912,
                    2,
                ]
                + [0] * 28,
                "skillEnable": [
                    575218834,
                    268435456,
                    536870912,
                    2,
                ]
                + [0] * 28,
                "slotMagicArts": [55, 57, 58, 56] + [0] * 4,
                "slotShortcutUser": [0] * 8,
                "slotShortcutMagicArts": [0] * 8,
                "condition": 0,
                "conditionTime": [0.0] * 32,
                "conditionEffect": [0.0] * 32,
                "bTipoEquip": False,
                "skillRecommendedType": 0,
                "firstName": "Milla",
                "partyType": 0,
                "costume": 67108941,
                "hair": 67108868,
                "attachment": [0] * 3,
                "attachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "attachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "attachmentTransform": [0] * 3,
                "totalExp": 0,
                "gp": 0,
                "formationIndex": {"x": 2.0, "y": 1.0},
                "baseResidueHPMax": 0.0,
                "baseResidueTPMax": 0.0,
                "baseResidueACMax": 0.0,
                "baseResidueSPMax": 0.0,
                "baseResidueStrength": 0.0,
                "baseResidueIntelligence": 0.0,
                "baseResidueStamina": 0.0,
                "baseResidueDexterity": 0.0,
                "baseResidueAgility": 0.0,
                "baseResidueSpirit": 0.0,
                "baseResidueLuck": 0.0,
                "counter": [0] * 16,
                "strategy": [1, 9, 16, 20, 25, 29, 33],
                "equipmentStack": [0, 0, 0, 0],
                "costumeStack": 0,
                "hairStack": 0,
                "attachmentStack": [0] * 3,
                "baseCoefficientHPMax": 0,
                "baseCoefficientTPMax": 0,
                "baseCoefficientACMax": 0,
                "baseCoefficientSPMax": 0,
                "baseCoefficientStrength": 0,
                "baseCoefficientIntelligence": 0,
                "baseCoefficientStamina": 0,
                "baseCoefficientDexterity": 0,
                "baseCoefficientAgility": 0,
                "baseCoefficientSpirit": 0,
                "baseCoefficientLuck": 0,
                "herbHPMax": 0,
                "herbTPMax": 0,
                "herbSPMax": 0,
                "herbStrength": 0,
                "herbIntelligence": 0,
                "herbStamina": 0,
                "herbDexterity": 0,
                "herbAgility": 0,
                "herbSpirit": 0,
            },
        },
        "mLinkInfo": {"condition": 0, "partner": 0, "colorPattern": 0, "frame": 0, "history": [0] * 6},
        "mGrowthStatus": {
            "mNodeFlag": [0] * 128,
            "mLineFlag": [0] * 128,
            "mPlaneFlag": [0] * 64,
            "mOrbLevel": [4] * 4,
            "mNodeNumFlag": [0] * 4,
            "mLineNumFlag": [0] * 4,
            "mPlaneNumFlag": [0] * 4,
            "mCurrentOrbSheet": 0,
            "mCurrentNode": [0] * 4,
            "mNumOrbSheet": 1,
            "mNumEnableMaxOrbSheet": 2,
        },
        "mAttachmentCustomData": [
            {
                "mCostume": 67108941,
                "mHair": 67108868,
                "mAttachment": [0] * 3,
                "mAttachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "mAttachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "mAttachmentTransform": [0] * 3,
            }
        ]
        * 8,
        "mGrowthTransferData": {"mNodeGettingOrder": []},
        "mGrowthTransferReferenceData": {"mNodeGettingOrder": []},
    }


def create_player3_status_save_dict() -> PlayerStatusSaveDataDict:
    return {
        "mPlayerStatusData": {
            "mVersion": 103,
            "mStatus": {
                "bParty": True,
                "partyID": 3,
                "level": 3,
                "hp": 472,
                "tp": 90,
                "ac": 0,
                "baseHPMax": 450,
                "baseTPMax": 90,
                "baseACMax": 4,
                "baseSPMax": 10,
                "baseStrength": 62,
                "baseIntelligence": 32,
                "baseStamina": 50,
                "baseDexterity": 47,
                "baseAgility": 40,
                "baseSpirit": 39,
                "baseLuck": 41,
                "elementEndurance": [100.0] * 6,
                "equipment": [0, 0, 0, 0],
                "magicArtsLearn": [0] * 2 + [1572864] + [0] * 61,
                "magicArtsEnable": [4294967295] * 64,
                "magicArtsCount": [0] * 2048,
                "skillLearn": [537395200] + [0] * 31,
                "skillEnable": [537395200] + [0] * 31,
                "slotMagicArts": [83, 84] + [0] * 6,
                "slotShortcutUser": [0] * 8,
                "slotShortcutMagicArts": [0] * 8,
                "condition": 0,
                "conditionTime": [0.0] * 32,
                "conditionEffect": [0.0] * 32,
                "bTipoEquip": False,
                "skillRecommendedType": 0,
                "firstName": "Alvin",
                "partyType": 0,
                "costume": 67108942,
                "hair": 67108869,
                "attachment": [0] * 3,
                "attachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "attachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "attachmentTransform": [0] * 3,
                "totalExp": 428,
                "gp": 7,
                "formationIndex": {"x": 1.0, "y": 0.0},
                "baseResidueHPMax": 0.0,
                "baseResidueTPMax": 0.0,
                "baseResidueACMax": 0.0,
                "baseResidueSPMax": 0.0,
                "baseResidueStrength": 0.0,
                "baseResidueIntelligence": 0.0,
                "baseResidueStamina": 0.0,
                "baseResidueDexterity": 0.0,
                "baseResidueAgility": 0.0,
                "baseResidueSpirit": 0.0,
                "baseResidueLuck": 0.0,
                "counter": [0] * 16,
                "strategy": [5, 9, 16, 20, 25, 29, 33],
                "equipmentStack": [0, 0, 0, 0],
                "costumeStack": 0,
                "hairStack": 0,
                "attachmentStack": [0] * 3,
                "baseCoefficientHPMax": 0,
                "baseCoefficientTPMax": 0,
                "baseCoefficientACMax": 0,
                "baseCoefficientSPMax": 0,
                "baseCoefficientStrength": 0,
                "baseCoefficientIntelligence": 0,
                "baseCoefficientStamina": 0,
                "baseCoefficientDexterity": 0,
                "baseCoefficientAgility": 0,
                "baseCoefficientSpirit": 0,
                "baseCoefficientLuck": 0,
                "herbHPMax": 0,
                "herbTPMax": 0,
                "herbSPMax": 0,
                "herbStrength": 0,
                "herbIntelligence": 0,
                "herbStamina": 0,
                "herbDexterity": 0,
                "herbAgility": 0,
                "herbSpirit": 0,
            },
        },
        "mLinkInfo": {"condition": 0, "partner": 0, "colorPattern": 0, "frame": 0, "history": [0] * 6},
        "mGrowthStatus": {
            "mNodeFlag": [0] * 128,
            "mLineFlag": [0] * 128,
            "mPlaneFlag": [0] * 64,
            "mOrbLevel": [4] * 4,
            "mNodeNumFlag": [0] * 4,
            "mLineNumFlag": [0] * 4,
            "mPlaneNumFlag": [0] * 4,
            "mCurrentOrbSheet": 0,
            "mCurrentNode": [0] * 4,
            "mNumOrbSheet": 1,
            "mNumEnableMaxOrbSheet": 2,
        },
        "mAttachmentCustomData": [
            {
                "mCostume": 67108942,
                "mHair": 67108869,
                "mAttachment": [0] * 3,
                "mAttachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "mAttachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "mAttachmentTransform": [0] * 3,
            }
        ]
        * 8,
        "mGrowthTransferData": {"mNodeGettingOrder": []},
        "mGrowthTransferReferenceData": {"mNodeGettingOrder": []},
    }


def create_player4_status_save_dict() -> PlayerStatusSaveDataDict:
    return {
        "mPlayerStatusData": {
            "mVersion": 103,
            "mStatus": {
                "bParty": True,
                "partyID": 4,
                "level": 1,
                "hp": 378,
                "tp": 115,
                "ac": 0,
                "baseHPMax": 360,
                "baseTPMax": 115,
                "baseACMax": 4,
                "baseSPMax": 10,
                "baseStrength": 40,
                "baseIntelligence": 54,
                "baseStamina": 35,
                "baseDexterity": 43,
                "baseAgility": 37,
                "baseSpirit": 61,
                "baseLuck": 95,
                "elementEndurance": [100.0] * 6,
                "equipment": [0, 0, 0, 0],
                "magicArtsLearn": [0] * 3 + [8404992] + [0] * 60,
                "magicArtsEnable": [4294967295] * 64,
                "magicArtsCount": [0] * 2048,
                "skillLearn": [524288] + [0] * 31,
                "skillEnable": [524288] + [0] * 31,
                "slotMagicArts": [119, 110] + [0] * 6,
                "slotShortcutUser": [0] * 8,
                "slotShortcutMagicArts": [0] * 8,
                "condition": 0,
                "conditionTime": [0.0] * 32,
                "conditionEffect": [0.0] * 32,
                "bTipoEquip": False,
                "skillRecommendedType": 0,
                "firstName": "Elize",
                "partyType": 0,
                "costume": 67108943,
                "hair": 67108870,
                "attachment": [0] * 3,
                "attachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "attachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "attachmentTransform": [0] * 3,
                "totalExp": 0,
                "gp": 0,
                "formationIndex": {"x": 1.0, "y": 3.0},
                "baseResidueHPMax": 0.0,
                "baseResidueTPMax": 0.0,
                "baseResidueACMax": 0.0,
                "baseResidueSPMax": 0.0,
                "baseResidueStrength": 0.0,
                "baseResidueIntelligence": 0.0,
                "baseResidueStamina": 0.0,
                "baseResidueDexterity": 0.0,
                "baseResidueAgility": 0.0,
                "baseResidueSpirit": 0.0,
                "baseResidueLuck": 0.0,
                "counter": [0] * 16,
                "strategy": [7, 12, 16, 20, 25, 31, 33],
                "equipmentStack": [0, 0, 0, 0],
                "costumeStack": 0,
                "hairStack": 0,
                "attachmentStack": [0] * 3,
                "baseCoefficientHPMax": 0,
                "baseCoefficientTPMax": 0,
                "baseCoefficientACMax": 0,
                "baseCoefficientSPMax": 0,
                "baseCoefficientStrength": 0,
                "baseCoefficientIntelligence": 0,
                "baseCoefficientStamina": 0,
                "baseCoefficientDexterity": 0,
                "baseCoefficientAgility": 0,
                "baseCoefficientSpirit": 0,
                "baseCoefficientLuck": 0,
                "herbHPMax": 0,
                "herbTPMax": 0,
                "herbSPMax": 0,
                "herbStrength": 0,
                "herbIntelligence": 0,
                "herbStamina": 0,
                "herbDexterity": 0,
                "herbAgility": 0,
                "herbSpirit": 0,
            },
        },
        "mLinkInfo": {"condition": 0, "partner": 0, "colorPattern": 0, "frame": 0, "history": [0] * 6},
        "mGrowthStatus": {
            "mNodeFlag": [0] * 128,
            "mLineFlag": [0] * 128,
            "mPlaneFlag": [0] * 64,
            "mOrbLevel": [4] * 4,
            "mNodeNumFlag": [0] * 4,
            "mLineNumFlag": [0] * 4,
            "mPlaneNumFlag": [0] * 4,
            "mCurrentOrbSheet": 0,
            "mCurrentNode": [0] * 4,
            "mNumOrbSheet": 1,
            "mNumEnableMaxOrbSheet": 2,
        },
        "mAttachmentCustomData": [
            {
                "mCostume": 67108943,
                "mHair": 67108870,
                "mAttachment": [0] * 3,
                "mAttachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "mAttachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "mAttachmentTransform": [0] * 3,
            }
        ]
        * 8,
        "mGrowthTransferData": {"mNodeGettingOrder": []},
        "mGrowthTransferReferenceData": {"mNodeGettingOrder": []},
    }


def create_player5_status_save_dict() -> PlayerStatusSaveDataDict:
    return {
        "mPlayerStatusData": {
            "mVersion": 103,
            "mStatus": {
                "bParty": True,
                "partyID": 5,
                "level": 4,
                "hp": 367,
                "tp": 120,
                "ac": 0,
                "baseHPMax": 350,
                "baseTPMax": 120,
                "baseACMax": 4,
                "baseSPMax": 10,
                "baseStrength": 37,
                "baseIntelligence": 64,
                "baseStamina": 38,
                "baseDexterity": 48,
                "baseAgility": 40,
                "baseSpirit": 43,
                "baseLuck": 29,
                "elementEndurance": [100.0] * 6,
                "equipment": [0, 0, 0, 0],
                "magicArtsLearn": [0] * 4 + [574464] + [0] * 59,
                "magicArtsEnable": [4294967295] * 64,
                "magicArtsCount": [0] * 2048,
                "skillLearn": [1611137024, 419430592, 4] + [0] * 29,
                "skillEnable": [524288, 268435456] + [0] * 30,
                "slotMagicArts": [142, 143, 138, 147] + [0] * 4,
                "slotShortcutUser": [0] * 8,
                "slotShortcutMagicArts": [0] * 8,
                "condition": 0,
                "conditionTime": [0.0] * 32,
                "conditionEffect": [0.0] * 32,
                "bTipoEquip": False,
                "skillRecommendedType": 0,
                "firstName": "Rowen",
                "partyType": 0,
                "costume": 67108944,
                "hair": 67108871,
                "attachment": [0] * 3,
                "attachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "attachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "attachmentTransform": [0] * 3,
                "totalExp": 656,
                "gp": 10,
                "formationIndex": {"x": 3.0, "y": 3.0},
                "baseResidueHPMax": 0.0,
                "baseResidueTPMax": 0.0,
                "baseResidueACMax": 0.0,
                "baseResidueSPMax": 0.0,
                "baseResidueStrength": 0.0,
                "baseResidueIntelligence": 0.0,
                "baseResidueStamina": 0.0,
                "baseResidueDexterity": 0.0,
                "baseResidueAgility": 0.0,
                "baseResidueSpirit": 0.0,
                "baseResidueLuck": 0.0,
                "counter": [0] * 16,
                "strategy": [8, 10, 16, 20, 25, 29, 33],
                "equipmentStack": [0, 0, 0, 0],
                "costumeStack": 0,
                "hairStack": 0,
                "attachmentStack": [0] * 3,
                "baseCoefficientHPMax": 0,
                "baseCoefficientTPMax": 0,
                "baseCoefficientACMax": 0,
                "baseCoefficientSPMax": 0,
                "baseCoefficientStrength": 0,
                "baseCoefficientIntelligence": 0,
                "baseCoefficientStamina": 0,
                "baseCoefficientDexterity": 0,
                "baseCoefficientAgility": 0,
                "baseCoefficientSpirit": 0,
                "baseCoefficientLuck": 0,
                "herbHPMax": 0,
                "herbTPMax": 0,
                "herbSPMax": 0,
                "herbStrength": 0,
                "herbIntelligence": 0,
                "herbStamina": 0,
                "herbDexterity": 0,
                "herbAgility": 0,
                "herbSpirit": 0,
            },
        },
        "mLinkInfo": {"condition": 0, "partner": 0, "colorPattern": 0, "frame": 0, "history": [0] * 6},
        "mGrowthStatus": {
            "mNodeFlag": [0] * 128,
            "mLineFlag": [0] * 128,
            "mPlaneFlag": [0] * 64,
            "mOrbLevel": [4] * 4,
            "mNodeNumFlag": [0] * 4,
            "mLineNumFlag": [0] * 4,
            "mPlaneNumFlag": [0] * 4,
            "mCurrentOrbSheet": 0,
            "mCurrentNode": [0] * 4,
            "mNumOrbSheet": 1,
            "mNumEnableMaxOrbSheet": 2,
        },
        "mAttachmentCustomData": [
            {
                "mCostume": 67108944,
                "mHair": 67108871,
                "mAttachment": [0] * 3,
                "mAttachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "mAttachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "mAttachmentTransform": [0] * 3,
            }
        ]
        * 8,
        "mGrowthTransferData": {"mNodeGettingOrder": []},
        "mGrowthTransferReferenceData": {"mNodeGettingOrder": []},
    }


def create_player6_status_save_dict() -> PlayerStatusSaveDataDict:
    return {
        "mPlayerStatusData": {
            "mVersion": 103,
            "mStatus": {
                "bParty": True,
                "partyID": 6,
                "level": 1,
                "hp": 410,
                "tp": 105,
                "ac": 0,
                "baseHPMax": 410,
                "baseTPMax": 105,
                "baseACMax": 4,
                "baseSPMax": 10,
                "baseStrength": 47,
                "baseIntelligence": 40,
                "baseStamina": 40,
                "baseDexterity": 41,
                "baseAgility": 52,
                "baseSpirit": 50,
                "baseLuck": 5,
                "elementEndurance": [100.0] * 6,
                "equipment": [0, 0, 0, 0],
                "magicArtsLearn": [0] * 5 + [2361600] + [0] * 58,
                "magicArtsEnable": [4294967295] * 64,
                "magicArtsCount": [0] * 2048,
                "skillLearn": [3792175104, 419430592, 4, 0, 0, 32768] + [0] * 26,
                "skillEnable": [3792175104] + [0] * 4 + [32768] + [0] * 26,
                "slotMagicArts": [168, 178, 171, 181] + [0] * 4,
                "slotShortcutUser": [0] * 8,
                "slotShortcutMagicArts": [0] * 8,
                "condition": 0,
                "conditionTime": [0.0] * 32,
                "conditionEffect": [0.0] * 32,
                "bTipoEquip": False,
                "skillRecommendedType": 0,
                "firstName": "Leia",
                "partyType": 0,
                "costume": 67108945,
                "hair": 67108872,
                "attachment": [0] * 3,
                "attachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "attachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "attachmentTransform": [0] * 3,
                "totalExp": 0,
                "gp": 0,
                "formationIndex": {"x": 2.0, "y": 2.0},
                "baseResidueHPMax": 0.0,
                "baseResidueTPMax": 0.0,
                "baseResidueACMax": 0.0,
                "baseResidueSPMax": 0.0,
                "baseResidueStrength": 0.0,
                "baseResidueIntelligence": 0.0,
                "baseResidueStamina": 0.0,
                "baseResidueDexterity": 0.0,
                "baseResidueAgility": 0.0,
                "baseResidueSpirit": 0.0,
                "baseResidueLuck": 0.0,
                "counter": [0] * 16,
                "strategy": [6, 12, 16, 20, 25, 29, 33],
                "equipmentStack": [0, 0, 0, 0],
                "costumeStack": 0,
                "hairStack": 0,
                "attachmentStack": [0] * 3,
                "baseCoefficientHPMax": 0,
                "baseCoefficientTPMax": 0,
                "baseCoefficientACMax": 0,
                "baseCoefficientSPMax": 0,
                "baseCoefficientStrength": 0,
                "baseCoefficientIntelligence": 0,
                "baseCoefficientStamina": 0,
                "baseCoefficientDexterity": 0,
                "baseCoefficientAgility": 0,
                "baseCoefficientSpirit": 0,
                "baseCoefficientLuck": 0,
                "herbHPMax": 0,
                "herbTPMax": 0,
                "herbSPMax": 0,
                "herbStrength": 0,
                "herbIntelligence": 0,
                "herbStamina": 0,
                "herbDexterity": 0,
                "herbAgility": 0,
                "herbSpirit": 0,
            },
        },
        "mLinkInfo": {"condition": 0, "partner": 0, "colorPattern": 0, "frame": 0, "history": [0] * 6},
        "mGrowthStatus": {
            "mNodeFlag": [0] * 128,
            "mLineFlag": [0] * 128,
            "mPlaneFlag": [0] * 64,
            "mOrbLevel": [4] * 4,
            "mNodeNumFlag": [0] * 4,
            "mLineNumFlag": [0] * 4,
            "mPlaneNumFlag": [0] * 4,
            "mCurrentOrbSheet": 0,
            "mCurrentNode": [0] * 4,
            "mNumOrbSheet": 1,
            "mNumEnableMaxOrbSheet": 2,
        },
        "mAttachmentCustomData": [
            {
                "mCostume": 67108945,
                "mHair": 67108872,
                "mAttachment": [0] * 3,
                "mAttachmentMatrix": [
                    Matrix(
                        e00=1.0,
                        e01=0.0,
                        e02=0.0,
                        e03=0.0,
                        e10=0.0,
                        e11=1.0,
                        e12=0.0,
                        e13=0.0,
                        e20=0.0,
                        e21=0.0,
                        e22=1.0,
                        e23=0.0,
                        e30=0.0,
                        e31=0.0,
                        e32=0.0,
                        e33=1.0,
                    )
                ]
                * 3,
                "mAttachmentColor": [Color(r=1.0, g=1.0, b=1.0, a=1.0)] * 3,
                "mAttachmentTransform": [0] * 3,
            }
        ]
        * 8,
        "mGrowthTransferData": {"mNodeGettingOrder": []},
        "mGrowthTransferReferenceData": {"mNodeGettingOrder": []},
    }
