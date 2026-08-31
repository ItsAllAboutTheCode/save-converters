"""
List of structures mapping to raw binary save file for Tales of Graces f
The TOGAPP.bin file is mapped to these structures
"""

from ctypes import c_float, c_uint8, c_uint16, c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_size
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    MarshalStructure,
    OffsetField,
)

# Save size of TOGAPP.bin which contains the binary data that is loaded by the game
GRACES_F_RAW_SAVE_SIZE = 79104


class PlayerLocationOffsetStruct(MarshalStructure):
    """Starts at offset 0x04"""

    _fields_ = [
        ("x", c_float),  # +0x0
        ("y", c_float),  # +0x4
        ("z", c_float),  # +0x8
        ("unknown_float1", c_float),  # +0xC
        ("padding1", c_uint8 * 4),  # +0x10
        ("map_id", c_uint32),  # +0x14
        ("padding2", c_uint8 * 4),  # +0x18
        ("unknown_int1", c_uint32),  # +0x1C
        ("unknown_data2", c_uint8 * 8),  # +0x20
        ("unknown_int2", c_uint32),  # +0x28
        # total 0x2C bytes
    ]


assert_struct_size(PlayerLocationOffsetStruct, 0x2C)


class GameDataStruct(MarshalStructure):
    """Starts at offset 0x30"""

    _fields_ = [
        ("party_formation", c_uint8 * 7),  # +0x0
        ("padding1", c_uint8),  # +0x7
        ("unplayable_characters", c_uint8 * 2),  # +0x8
        ("unknown_data1", c_uint8 * 6),  # +0xA
        ("padding2", c_uint8 * 4),  # +0x10
        ("unknown_data2", c_uint8 * 4),  # +0x14
        ("padding3", c_uint8 * 4),  # +0x18
        ("unknown_data3", c_uint8 * 4),  # +0x1C
        ("unknown_data4", c_uint8 * 16),  # +0x20
        ("padding4", c_uint8 * 4),  # +0x30
        # total 0x34 bytes
    ]


assert_struct_size(GameDataStruct, 0x34)


class CharacterDataStats(MarshalStructure):
    """Starts at offset 0x84"""

    _fields_ = [
        ("curr_exp", c_uint32),  # +0x0
        ("exp_to_next_level", c_uint32),  # +0x4
        ("level", c_uint32),  # +0x8
        ("character_id", c_uint32),  # +0xC
        ("padding1", c_uint32 * 2),  # +0x10
        ("current_hp", c_uint32),  # +0x18
        ("padding2", c_uint32),  # +0x1C
        ("herb_p_atk", c_float),  # +0x20
        ("herb_c_atk", c_float),  # +0x24
        ("herb_acc", c_float),  # +0x28
        ("herb_p_def", c_float),  # +0x2C
        ("herb_c_def", c_float),  # +0x30
        ("herb_c_eva", c_float),  # +0x34
        ("herb_max_hp", c_float),  # +0x38
        ("unknown_float1", c_float),  # +0x3C
        ("base_p_atk", c_float),  # +0x40
        ("base_c_atk", c_float),  # +0x44
        ("base_acc", c_float),  # +0x48
        ("base_p_def", c_float),  # +0x4C
        ("base_c_def", c_float),  # +0x50
        ("base_eva", c_float),  # +0x54
        ("base_max_hp", c_float),  # +0x58
        # total 0x5C bytes
    ]


assert_struct_size(CharacterDataStats, 0x5C)


class CharacterDataCurrEquipment(MarshalStructure):
    """Starts at offset 0x108"""

    _fields_ = [
        ("id", c_uint16),  # +0x0
        ("weapon_id", c_uint16),  # +0x2
        ("armor_id", c_uint16),  # +0x4
        ("unique_id", c_uint16),  # +0x6
        ("gem_id", c_uint16),  # +0x8
        ("title_id", c_uint16),  # +0xA
        ("current_title_sp", c_uint32),  # +0xC
        # total 0x10 bytes
    ]


assert_struct_size(CharacterDataCurrEquipment, 0x10)


class CharacterDataTitle(MarshalStructure):
    """Starts at offset 0x118"""

    _fields_ = [
        ("id", c_uint16),  # +0x0
        ("curr_mastery_level", c_uint8),  # +0x2
        ("max_mastery_level", c_uint8),  # +0x3
        ("curr_sp", c_uint32),  # +0x4
        # total 0x8 bytes
    ]


assert_struct_size(CharacterDataTitle, 0x8)


class CharacterDataTitleArray(MarshalStructure):
    """Starts at offset 0x118"""

    _fields_ = [
        ("titles", CharacterDataTitle * 200),  # +0x0
        # total 0x640 bytes
    ]


assert_struct_size(CharacterDataTitleArray, 0x640)


class CharacterDataArte(MarshalStructure):
    """Starts at offset 0x758"""

    _fields_ = [
        ("marker", c_uint8 * 2),  # +0x0 appears to be hardcoded to 91 00
        ("unknown_data1", c_uint8 * 2),  # +0x2
        ("unknown_data2", c_uint8 * 2),  # +0x4
        ("unknown_data3", c_uint8 * 2),  # +0x6
        ("unknown_data4", c_uint8 * 2),  # +0x8
        ("usage", c_uint16),  # +0xA
        # total 0xC bytes
    ]


assert_struct_size(CharacterDataArte, 0xC)


class CharacterDataArteArray(MarshalStructure):
    """Starts at offset 0x758"""

    _fields_ = [
        ("artes", CharacterDataArte * 64),  # +0x0
        # total 0x300 bytes
    ]


assert_struct_size(CharacterDataArteArray, 0x300)


class CharacterDataStruct(MarshalStructure):
    """Starts at offset 0x64"""

    _fields_ = [
        ("name", c_uint8 * 32),  # +0x0
        ("stats", CharacterDataStats),  # +0x20
        ("padding1", c_uint8 * 4),  # +0x7C
        ("unknown_float1", c_float),  # +0x80
        ("padding2", c_uint32 * 3),  # +0x84
        ("unknown_float2", c_float),  # +0x90
        ("padding3", c_uint32 * 3),  # +0x94
        ("unknown_float3", c_float),  # +0xA0
        ("curr_equip", CharacterDataCurrEquipment),  # +0xA4
        ("titles", CharacterDataTitleArray),  # +0xB4
        ("artes", CharacterDataArteArray),  # +0x6F4
        ("unknown_shorts1", c_uint16 * 4),  # +0x9E4
        ("padding4", c_uint8 * 0x1CC),  # +0x9EC
        ("unknown_int1", c_uint32),  # +0xBB8
        ("unknown_int2", c_uint32),  # +0xBD0
        ("padding5", c_uint32 * 2),  # +0xBCC
        # total 0xBD8 bytes
    ]


assert_struct_size(CharacterDataStruct, 0xBD8)


class CharacterDataStructArray(MarshalStructure):
    """Starts at offset 0x64
    Stride between characters is 0xBD8 = 3032
    There are 10 character entries
    """

    _fields_ = [
        ("Asbel", CharacterDataStruct),  # +0x0
        ("Sophie", CharacterDataStruct),  # +0xBD8
        ("Hubert", CharacterDataStruct),  # +0x17B0
        ("Cheria", CharacterDataStruct),  # +0x2388
        ("Malik", CharacterDataStruct),  # +0x2F60
        ("Pascal", CharacterDataStruct),  # +0x3B38
        ("Richard", CharacterDataStruct),  # +0x4710
        ("Asbel (kid)", CharacterDataStruct),  # +0x52E8
        ("Hubert (kid)", CharacterDataStruct),  # +0x5EC0
        ("Richard (kid)", CharacterDataStruct),  # +0x6A98
        # total 0x7670
    ]


assert_struct_size(CharacterDataStructArray, 0x7670)


class GaldDataStruct(MarshalStructure):
    """Starts at offset 0x76D4"""

    _fields_ = [
        ("gald", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(GaldDataStruct, 0x4)


class PlaytimeDataStruct(MarshalStructure):
    """Starts at offset 0x76D8"""

    _fields_ = [
        ("playtime", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(PlaytimeDataStruct, 0x4)


class ShardData(MarshalStructure):
    """Starts at offset 0x76DC"""

    _fields_ = [
        ("id", c_uint16),  # +0x0
        ("quality_id", c_uint8),  # +0x5
        ("rank", c_uint8),  # +0x6
        # total 0x4 bytes
    ]


assert_struct_size(ShardData, 0x4)


class ShardDataArray(MarshalStructure):
    """Starts at offset 0x76DC
    Stride between shard is 4
    There are 202 entries
    """

    _fields_ = [
        ("shard", ShardData * 202),  # +0x0
        # total 0x328
    ]


assert_struct_size(ShardDataArray, 0x328)


class WeaponData(MarshalStructure):
    """Starts at offset 0x7A04"""

    _fields_ = [
        ("id", c_uint16),  # +0x0
        ("additional_p_atk", c_uint16),  # +0x2
        ("additional_c_atk", c_uint16),  # +0x4
        ("additional_c_acc", c_uint16),  # +0x6
        ("min_cc", c_uint8),  # +0x8
        ("max_cc", c_uint8),  # +0x9
        ("sell_price", c_uint16),  # +0xA
        ("shard1_id", c_uint8),  # +0xC
        ("shard1_rank", c_uint8),  # +0xD
        ("shard2_id", c_uint8),  # +0xE
        ("shard2_rank", c_uint8),  # +0xF
        ("quality_id", c_uint8),  # +0x10
        ("unknown_byte1", c_uint8),  # +0x11
        ("equipped_by_char_id", c_uint8),  # +0x12
        ("unknown_byte2", c_uint8),  # +0x13
        ("battles_with_weapon", c_uint16),  # +0x14
        ("+ mark value(weapon tempered)", c_uint16),  # +0x16
        ("unknown_bytes3", c_uint8 * 2),  # +0x18
        # total 0x1A bytes
    ]


assert_struct_size(WeaponData, 0x1A)


class WeaponDataArray(MarshalStructure):
    """Starts at offset 0x7A04
    Stride between weapons is 26
    There are 202 entries
    """

    _fields_ = [
        ("weapons", WeaponData * 202),  # +0x0
        # total 0x1484
    ]


assert_struct_size(WeaponDataArray, 0x1484)


class ArmorData(MarshalStructure):
    """Starts at offset 0x8E88"""

    _fields_ = [
        ("id", c_uint16),  # +0x0
        ("additional_p_def", c_uint16),  # +0x2
        ("additional_c_def", c_uint16),  # +0x4
        ("additional_c_eva", c_uint16),  # +0x6
        ("sell_price", c_uint16),  # +0x8
        ("shard1_id", c_uint8),  # +0xA
        ("shard1_rank", c_uint8),  # +0xB
        ("shard2_id", c_uint8),  # +0xC
        ("shard2_rank", c_uint8),  # +0xD
        ("quality_id", c_uint8),  # +0xE
        ("unknown_byte1", c_uint8),  # +0xF
        ("equipped_by_char_id", c_uint8),  # +0x10
        ("unknown_byte2", c_uint8),  # +0x11
        ("battles_with_armor", c_uint16),  # +0x12
        ("+ mark value(weapon tempered)", c_uint16),  # +0x14
        # total 0x16 bytes
    ]


assert_struct_size(ArmorData, 0x16)


class ArmorDataArray(MarshalStructure):
    """Starts at offset 0x8E88
    Stride between armor is 22
    There are 202 entries
    """

    _fields_ = [
        ("armor", ArmorData * 202),  # +0x0
        # total 0x115C
    ]


assert_struct_size(ArmorDataArray, 0x115C)


class GemData(MarshalStructure):
    """Starts at offset 0x9FE4"""

    _fields_ = [
        ("id", c_uint16),  # +0x0
        ("shard1_id", c_uint8),  # +0x2
        ("shard1_rank", c_uint8),  # +0x3
        ("shard2_id", c_uint8),  # +0x4
        ("shard2_rank", c_uint8),  # +0x5
        ("quality_id", c_uint8),  # +0x6
        ("equipped_by_char_id", c_uint8),  # +0x7
        # total 0x8 bytes
    ]


assert_struct_size(GemData, 0x8)


class GemDataArray(MarshalStructure):
    """Starts at offset 0x9FE4
    Stride between gem is 8
    There are 202 entries
    """

    _fields_ = [
        ("gem", GemData * 202),  # +0x0
        # total 0x650
    ]


assert_struct_size(GemDataArray, 0x650)


class ItemAmountStruct(MarshalStructure):
    """Represents the count of an item"""

    _fields_ = [
        ("count", c_uint8),  # +0x0
        # total 0x1 byte
    ]


assert_struct_size(ItemAmountStruct, 0x1)


class UnknownItemsArrayStruct(MarshalStructure):
    """Starts at offset 0xA634"""

    _fields_ = [
        ("other", ItemAmountStruct * 13),  # +0x0
        # total 0xD bytes
    ]


assert_struct_size(UnknownItemsArrayStruct, 0xD)


class ConsumablesItemsArrayStruct(MarshalStructure):
    """Starts at offset 0xA641"""

    _fields_ = [
        ("Apple Gel", ItemAmountStruct),  # +0x0
        ("Peach Gel", ItemAmountStruct),
        ("Grape Gel", ItemAmountStruct),
        ("Melon Gel", ItemAmountStruct),
        ("Panacea Bottle", ItemAmountStruct),
        ("Syrup Bottle", ItemAmountStruct),
        ("Life Bottle", ItemAmountStruct),
        ("Elixir", ItemAmountStruct),
        ("All-Divide", ItemAmountStruct),
        ("Hourglass", ItemAmountStruct),
        ("Drop Bottle", ItemAmountStruct),
        ("Arcane Bottle", ItemAmountStruct),
        ("Holy Bottle", ItemAmountStruct),
        ("Dark Bottle", ItemAmountStruct),
        ("Sage", ItemAmountStruct),
        ("Lavender", ItemAmountStruct),
        ("Verbena", ItemAmountStruct),
        ("Rosemary", ItemAmountStruct),
        ("Saffron", ItemAmountStruct),
        ("Chamomile", ItemAmountStruct),
        ("Savory", ItemAmountStruct),
        ("Red Sage", ItemAmountStruct),
        ("Red Lavender", ItemAmountStruct),
        ("Red Verbena", ItemAmountStruct),
        ("Red Rosemary", ItemAmountStruct),
        ("Red Saffron", ItemAmountStruct),
        ("Red Chamomile", ItemAmountStruct),
        ("Red Savory", ItemAmountStruct),
        ("Mastery Tonic C", ItemAmountStruct),
        ("Mastery Tonic EX", ItemAmountStruct),
        ("Mastery Tonic G", ItemAmountStruct),
        ("Eleth Bottle C", ItemAmountStruct),
        ("Eleth Bottle EX", ItemAmountStruct),
        ("Eleth Bottle G", ItemAmountStruct),
        ("Ice Pop", ItemAmountStruct),
        ("padding1", c_uint8 * 1),  # +0x7B
        # total 0x24 bytes
    ]


assert_struct_size(ConsumablesItemsArrayStruct, 0x24)


class DishesArrayStruct(MarshalStructure):
    """Starts at offset 0xA665"""

    _fields_ = [
        ("Rice Ball", ItemAmountStruct),  # +0x0
        ("Plum Rice Ball", ItemAmountStruct),
        ("Roe Rice Ball", ItemAmountStruct),
        ("Salmon Rice Ball", ItemAmountStruct),
        ("Fried Rice", ItemAmountStruct),
        ("Crab Fried Rice", ItemAmountStruct),
        ("Doria", ItemAmountStruct),
        ("Paella", ItemAmountStruct),
        ("Bouillabaisse", ItemAmountStruct),
        ("Fisherman's Rice", ItemAmountStruct),
        ("Sweet and Sour Eel", ItemAmountStruct),
        ("Natto Rice", ItemAmountStruct),
        ("Rice Porridge", ItemAmountStruct),
        ("Plum Porridge", ItemAmountStruct),
        ("Salmon Porridge", ItemAmountStruct),
        ("Sea Bream Porridge", ItemAmountStruct),
        ("Eel Porridge", ItemAmountStruct),
        ("Grilled Chicken Bowl", ItemAmountStruct),
        ("Chicken and Egg Bowl", ItemAmountStruct),
        ("Pork Cutlet Bowl", ItemAmountStruct),
        ("Roe Bowl", ItemAmountStruct),
        ("Beef Bowl", ItemAmountStruct),
        ("Tuna Bowl", ItemAmountStruct),
        ("Salmon and Roe Bowl", ItemAmountStruct),
        ("Sushi Roll", ItemAmountStruct),
        ("Natto Roll", ItemAmountStruct),
        ("Omelette", ItemAmountStruct),
        ("Rice Omelette", ItemAmountStruct),
        ("Soba Omelette", ItemAmountStruct),
        ("Pizza", ItemAmountStruct),
        ("Pasta Carbonara", ItemAmountStruct),
        ("Meat Sauce Pasta", ItemAmountStruct),
        ("Pasta Vongole", ItemAmountStruct),
        ("Yakisoba Noodles", ItemAmountStruct),
        ("Sandwich", ItemAmountStruct),
        ("French Toast", ItemAmountStruct),
        ("Grilled Cheese", ItemAmountStruct),
        ("Pudding Cake", ItemAmountStruct),
        ("Natto on Toast", ItemAmountStruct),
        ("Fried Manju", ItemAmountStruct),
        ("Potato Salad", ItemAmountStruct),
        ("Baked Potato", ItemAmountStruct),
        ("Gratin", ItemAmountStruct),
        ("Soup au Gratin", ItemAmountStruct),
        ("Pasta au Gratin", ItemAmountStruct),
        ("Croquettes", ItemAmountStruct),
        ("Beef Croquettes", ItemAmountStruct),
        ("Crab Croquettes", ItemAmountStruct),
        ("Steak", ItemAmountStruct),
        ("Radish Steak", ItemAmountStruct),
        ("Marbled Steak", ItemAmountStruct),
        ("Marbled Radish Steak", ItemAmountStruct),
        ("Salisbury Steak", ItemAmountStruct),
        ("Radish Salisbury Steak", ItemAmountStruct),
        ("Tofu Salisbury Steak", ItemAmountStruct),
        ("Hamburger", ItemAmountStruct),
        ("Cheeseburger", ItemAmountStruct),
        ("Double Cheeseburger", ItemAmountStruct),
        ("Cabbage Rolls", ItemAmountStruct),
        ("Scottish Eggs", ItemAmountStruct),
        ("Fried Chicken", ItemAmountStruct),
        ("Twice Cooked Pork", ItemAmountStruct),
        ("Pork Potato Stew", ItemAmountStruct),
        ("Beef Potato Stew", ItemAmountStruct),
        ("Beef with Red Wine Sauce", ItemAmountStruct),
        ("Dry Curry", ItemAmountStruct),
        ("Curry", ItemAmountStruct),
        ("Pork Curry", ItemAmountStruct),
        ("Chicken Curry", ItemAmountStruct),
        ("Beef Curry", ItemAmountStruct),
        ("Seafood Curry", ItemAmountStruct),
        ("Stew", ItemAmountStruct),
        ("Beef Stew", ItemAmountStruct),
        ("Seafood Stew", ItemAmountStruct),
        ("Pot au Feu", ItemAmountStruct),
        ("Borscht", ItemAmountStruct),
        ("Fish &amp; Chips", ItemAmountStruct),
        ("Salmon Pie", ItemAmountStruct),
        ("Chili Shrimp", ItemAmountStruct),
        ("Curried Cod", ItemAmountStruct),
        ("Miso-Glazed Cod", ItemAmountStruct),
        ("Crablettes", ItemAmountStruct),
        ("Seafood Salad", ItemAmountStruct),
        ("Clam Miso Soup", ItemAmountStruct),
        ("Radish Miso Soup", ItemAmountStruct),
        ("Tofu Miso Soup", ItemAmountStruct),
        ("Beef Tofu", ItemAmountStruct),
        ("Mabo Tofu", ItemAmountStruct),
        ("Mabo Eggplant", ItemAmountStruct),
        ("Mabo Curry", ItemAmountStruct),
        ("Dashi Stew", ItemAmountStruct),
        ("Miso Stew", ItemAmountStruct),
        ("Quiche", ItemAmountStruct),
        ("Apple Pie", ItemAmountStruct),
        ("Pumpkin Pie", ItemAmountStruct),
        ("Banana Pie", ItemAmountStruct),
        ("Meat Pie", ItemAmountStruct),
        ("Peach Pie", ItemAmountStruct),
        ("Chocolate Pie", ItemAmountStruct),
        ("Apple Parfait", ItemAmountStruct),
        ("Tomato Parfait", ItemAmountStruct),
        ("Peach Parfait", ItemAmountStruct),
        ("Grape Parfait", ItemAmountStruct),
        ("Cheesecake", ItemAmountStruct),
        ("Pudding", ItemAmountStruct),
        ("Pumpkin Pudding", ItemAmountStruct),
        ("Truffle", ItemAmountStruct),
        ("Chocolate-Covered Banana", ItemAmountStruct),
        ("Chocolate Pudding", ItemAmountStruct),
        ("padding1", c_uint8 * 15),  # +0x6D
        # total 0x7C bytes
    ]


assert_struct_size(DishesArrayStruct, 0x7C)


class MaterialsArrayStruct(MarshalStructure):
    """Starts at offset 0xA6E1"""

    _fields_ = [
        ("Soaring Crystal", ItemAmountStruct),
        ("Wriggler Crystal", ItemAmountStruct),
        ("Submerged Crystal", ItemAmountStruct),
        ("Seascale Crystal", ItemAmountStruct),
        ("Overgrown Crystal", ItemAmountStruct),
        ("Fangtear Crystal", ItemAmountStruct),
        ("Formless Crystal", ItemAmountStruct),
        ("Mighty Crystal", ItemAmountStruct),
        ("Bloodsucker Crystal", ItemAmountStruct),
        ("Possessed Crystal", ItemAmountStruct),
        ("Reticent Crystal", ItemAmountStruct),
        ("Glacierfall Crystal", ItemAmountStruct),
        ("Hyperdense Crystal", ItemAmountStruct),
        ("High-Grade Crystal", ItemAmountStruct),
        ("Artificial Crystal", ItemAmountStruct),
        ("Violent Crystal", ItemAmountStruct),
        ("Blazing Crystal", ItemAmountStruct),
        ("Moist Crystal", ItemAmountStruct),
        ("Earthshudder Crystal", ItemAmountStruct),
        ("Bluster Crystal", ItemAmountStruct),
        ("Lightshimmer Crystal", ItemAmountStruct),
        ("Darkshine Crystal", ItemAmountStruct),
        ("Epic Neck", ItemAmountStruct),
        ("Kitty's Paw", ItemAmountStruct),
        ("Gillshiner", ItemAmountStruct),
        ("Charbroiler", ItemAmountStruct),
        ("Forktorquer", ItemAmountStruct),
        ("Pondslopper", ItemAmountStruct),
        ("Enasphere", ItemAmountStruct),
        ("Diosphere", ItemAmountStruct),
        ("Triasphere", ItemAmountStruct),
        ("Tesserasphere", ItemAmountStruct),
        ("Pentesphere", ItemAmountStruct),
        ("Eksisphere", ItemAmountStruct),
        ("Core Dust", ItemAmountStruct),
        ("Core Fragment", ItemAmountStruct),
        ("Clear Core", ItemAmountStruct),
        ("Luminous Core", ItemAmountStruct),
        ("Fur", ItemAmountStruct),
        ("Fancy Fur", ItemAmountStruct),
        ("Finest Fur", ItemAmountStruct),
        ("Fantabulous Fur", ItemAmountStruct),
        ("Feather", ItemAmountStruct),
        ("Pretty Feather", ItemAmountStruct),
        ("Elegant Feather", ItemAmountStruct),
        ("Alluring Feather", ItemAmountStruct),
        ("Nameless Seed", ItemAmountStruct),
        ("Anonymous Seed", ItemAmountStruct),
        ("Secret Seed", ItemAmountStruct),
        ("Classified Seed", ItemAmountStruct),
        ("Mysterious Liquid", ItemAmountStruct),
        ("Hazardous Liquid", ItemAmountStruct),
        ("Dangerous Liquid", ItemAmountStruct),
        ("Perilous Liquid", ItemAmountStruct),
        ("Scale", ItemAmountStruct),
        ("Hard Scale", ItemAmountStruct),
        ("Dragon Scale", ItemAmountStruct),
        ("Mythical Scale", ItemAmountStruct),
        ("Shattered Bone", ItemAmountStruct),
        ("Strong Bone", ItemAmountStruct),
        ("Amazing Bone", ItemAmountStruct),
        ("Incredible Bone", ItemAmountStruct),
        ("Broken Gear", ItemAmountStruct),
        ("Working Gear", ItemAmountStruct),
        ("Strange Gear", ItemAmountStruct),
        ("Arcane Gear", ItemAmountStruct),
        ("Decaying Fang", ItemAmountStruct),
        ("Pointy Fang", ItemAmountStruct),
        ("Sharp Fang", ItemAmountStruct),
        ("Killer Fang", ItemAmountStruct),
        ("Rusted Nail", ItemAmountStruct),
        ("Busted Blade", ItemAmountStruct),
        ("Decaying Sword", ItemAmountStruct),
        ("Corrupted Edge", ItemAmountStruct),
        ("Poison Needle", ItemAmountStruct),
        ("Venomous Needle", ItemAmountStruct),
        ("Killer Needle", ItemAmountStruct),
        ("Needle of Extinction", ItemAmountStruct),
        ("Seashell", ItemAmountStruct),
        ("Whirling Seashell", ItemAmountStruct),
        ("Crystal Seashell", ItemAmountStruct),
        ("Giant's Shield", ItemAmountStruct),
        ("Wood Chunk", ItemAmountStruct),
        ("Fine Wood", ItemAmountStruct),
        ("Golden Bough", ItemAmountStruct),
        ("Godwood", ItemAmountStruct),
        ("Chipped Claw", ItemAmountStruct),
        ("Sharp Claw", ItemAmountStruct),
        ("Emperor's Claw", ItemAmountStruct),
        ("Demon's Claw", ItemAmountStruct),
        ("Quarry Stone", ItemAmountStruct),
        ("Upper Quarry Stone", ItemAmountStruct),
        ("Earthen Pot", ItemAmountStruct),
        ("Meteorite", ItemAmountStruct),
        ("Dragon's Blood", ItemAmountStruct),
        ("Darkened Ore", ItemAmountStruct),
        ("Purebright Cloth", ItemAmountStruct),
        ("Otherworldly Seed", ItemAmountStruct),
        ("Water of Absolution", ItemAmountStruct),
        ("Morino Flower", ItemAmountStruct),
        ("Deathglow Algae", ItemAmountStruct),
        ("Puffpetal Down", ItemAmountStruct),
        ("Truth Salt", ItemAmountStruct),
        ("Strahtan Cactus", ItemAmountStruct),
        ("Kaigar's Script", ItemAmountStruct),
        ("Gel Seed", ItemAmountStruct),
        ("Common Metal", ItemAmountStruct),
        ("Rare Metal", ItemAmountStruct),
        ("Legendary Metal", ItemAmountStruct),
        ("Torchflame", ItemAmountStruct),
        ("Icicle", ItemAmountStruct),
        ("Lump of Clay", ItemAmountStruct),
        ("Torn Page", ItemAmountStruct),
        ("Strahteme Horn", ItemAmountStruct),
        ("Win Stick", ItemAmountStruct),
        ("Lose Stick", ItemAmountStruct),
        ("Jade Figure", ItemAmountStruct),
        ("Silver Figure", ItemAmountStruct),
        ("Seablue Figure", ItemAmountStruct),
        ("Amber Figure", ItemAmountStruct),
        ("Abyssal Figure", ItemAmountStruct),
        ("Scarlet Figure", ItemAmountStruct),
        ("Golden Figure", ItemAmountStruct),
        # total 0x7B bytes
    ]


assert_struct_size(MaterialsArrayStruct, 0x7B)


class CashablesArrayStruct(MarshalStructure):
    """Starts at offset 0xA75C"""

    _fields_ = [
        ("Glowfruit", ItemAmountStruct),  # +0x0
        ("Tanned Leather", ItemAmountStruct),
        ("Hairpin", ItemAmountStruct),
        ("Poison Fruit", ItemAmountStruct),
        ("Pyrogen", ItemAmountStruct),
        ("Ring", ItemAmountStruct),
        ("Animal Glue", ItemAmountStruct),
        ("Music Box", ItemAmountStruct),
        ("Horn", ItemAmountStruct),
        ("Fly Lure", ItemAmountStruct),
        ("Poison Brew", ItemAmountStruct),
        ("Shell Chalk", ItemAmountStruct),
        ("Fishing Rod", ItemAmountStruct),
        ("Earring", ItemAmountStruct),
        ("Stone Clock", ItemAmountStruct),
        ("Lantern", ItemAmountStruct),
        ("Vellum", ItemAmountStruct),
        ("Quill Pen", ItemAmountStruct),
        ("Deathwing Wine", ItemAmountStruct),
        ("Fine File", ItemAmountStruct),
        ("Collar Frills", ItemAmountStruct),
        ("Gelatin", ItemAmountStruct),
        ("Gear Puzzle", ItemAmountStruct),
        ("Bracelet", ItemAmountStruct),
        ("Kitchen Knife", ItemAmountStruct),
        ("Caustic", ItemAmountStruct),
        ("Bone Key", ItemAmountStruct),
        ("Spirit Mask", ItemAmountStruct),
        ("Necklace", ItemAmountStruct),
        ("Expensive Desk", ItemAmountStruct),
        ("Imperial Egg", ItemAmountStruct),
        ("Fireproof Cloth", ItemAmountStruct),
        ("Wings of Icarus", ItemAmountStruct),
        ("The Theory of Evolution", ItemAmountStruct),
        ("Soft Stone", ItemAmountStruct),
        ("Black Ring", ItemAmountStruct),
        ("Hand of Glory", ItemAmountStruct),
        ("Deicide Blade", ItemAmountStruct),
        ("White Ring", ItemAmountStruct),
        ("Damascus Steel", ItemAmountStruct),
        ("Cantarella", ItemAmountStruct),
        ("All-Seeing Eye", ItemAmountStruct),
        ("Demonsbane Arrow", ItemAmountStruct),
        ("Decisive Dice", ItemAmountStruct),
        ("Arc of the Covenant", ItemAmountStruct),
        ("Ashen Ring", ItemAmountStruct),
        ("Stream Rod", ItemAmountStruct),
        ("Carbon Rod", ItemAmountStruct),
        ("Neptune's Rod", ItemAmountStruct),
        ("Balloon Cloth", ItemAmountStruct),
        ("Stuffed Doll", ItemAmountStruct),
        ("Annals of the Almesera", ItemAmountStruct),
        ("Imperial Crest", ItemAmountStruct),
        ("Toxic Fluid", ItemAmountStruct),
        ("Stinky Bag", ItemAmountStruct),
        ("Rainbow Lens", ItemAmountStruct),
        ("Magical Mirror", ItemAmountStruct),
        ("Bizarre Clump", ItemAmountStruct),
        ("Knightwater", ItemAmountStruct),
        ("Frying Pan", ItemAmountStruct),
        ("Suspicious Powder", ItemAmountStruct),
        ("Heavenly Ore", ItemAmountStruct),
        ("Feather Badge", ItemAmountStruct),
        ("Masklike Object", ItemAmountStruct),
        ("Expensive Crown", ItemAmountStruct),
        ("Everlight", ItemAmountStruct),
        # total 0x42 bytes
    ]


assert_struct_size(CashablesArrayStruct, 0x42)


class IngredientsArrayStruct(MarshalStructure):
    """Starts at offset 0xA79E"""

    _fields_ = [
        ("Tomato", ItemAmountStruct),  # +0x0
        ("Lettuce", ItemAmountStruct),
        ("Onion", ItemAmountStruct),
        ("Potato", ItemAmountStruct),
        ("Carrot", ItemAmountStruct),
        ("Cabbage", ItemAmountStruct),
        ("Pumpkin", ItemAmountStruct),
        ("Radish", ItemAmountStruct),
        ("Eggplant", ItemAmountStruct),
        ("Melon", ItemAmountStruct),
        ("Apple", ItemAmountStruct),
        ("Peach", ItemAmountStruct),
        ("Grapes", ItemAmountStruct),
        ("Banana", ItemAmountStruct),
        ("Chicken", ItemAmountStruct),
        ("Pork", ItemAmountStruct),
        ("Beef", ItemAmountStruct),
        ("High-Grade Beef", ItemAmountStruct),
        ("Minced Meat", ItemAmountStruct),
        ("Tuna", ItemAmountStruct),
        ("Clam", ItemAmountStruct),
        ("Roe", ItemAmountStruct),
        ("Shrimp", ItemAmountStruct),
        ("Salmon", ItemAmountStruct),
        ("Crab", ItemAmountStruct),
        ("Cod", ItemAmountStruct),
        ("Eel", ItemAmountStruct),
        ("Sea Bream", ItemAmountStruct),
        ("Rice", ItemAmountStruct),
        ("Bread", ItemAmountStruct),
        ("Pasta", ItemAmountStruct),
        ("Pie Sheet", ItemAmountStruct),
        ("Veggie Set", ItemAmountStruct),
        ("Seafood Set", ItemAmountStruct),
        ("Spice Set", ItemAmountStruct),
        ("Egg", ItemAmountStruct),
        ("Milk", ItemAmountStruct),
        ("Cheese", ItemAmountStruct),
        ("Pickled Plum", ItemAmountStruct),
        ("Dried Seaweed", ItemAmountStruct),
        ("Tofu", ItemAmountStruct),
        ("Natto", ItemAmountStruct),
        ("Miso", ItemAmountStruct),
        ("Chocolate", ItemAmountStruct),
        ("Tea Leaves", ItemAmountStruct),
        ("Red Wine", ItemAmountStruct),
        ("White Wine", ItemAmountStruct),
        ("padding", c_uint8),
        # total 0x30 bytes
    ]


assert_struct_size(IngredientsArrayStruct, 0x30)


class EquipItemsArrayStruct(MarshalStructure):
    """Starts at offset 0xA801"""

    class WeaponsStruct(MarshalStructure):
        """Starts at offset 0xA801"""

        _fields_ = [
            ("Aston's Sword", ItemAmountStruct),  # +0x0
            ("Baronan Sword", ItemAmountStruct),
            ("Long Sword", ItemAmountStruct),
            ("Iron Sword", ItemAmountStruct),
            ("Steel Sword", ItemAmountStruct),
            ("Rune Sword", ItemAmountStruct),
            ("Battle Sword", ItemAmountStruct),
            ("Platinum Sword", ItemAmountStruct),
            ("Mythril Sword", ItemAmountStruct),
            ("Rare Sword", ItemAmountStruct),
            ("Katana", ItemAmountStruct),
            ("Flamberge", ItemAmountStruct),
            ("Zephyrus", ItemAmountStruct),
            ("Ice Coffin", ItemAmountStruct),
            ("Balmung", ItemAmountStruct),
            ("Durandal", ItemAmountStruct),
            ("Isleberg", ItemAmountStruct),
            ("Excalibur", ItemAmountStruct),
            ("Laevatein", ItemAmountStruct),
            ("Disintegrator", ItemAmountStruct),
            ("Valkyraffe", ItemAmountStruct),
            ("Devil's Crescent", ItemAmountStruct),
            ("Radiant Howl", ItemAmountStruct),
            ("Phact Phantasia", ItemAmountStruct),
            ("Gauntlets", ItemAmountStruct),
            ("Iron Gauntlets", ItemAmountStruct),
            ("Steel Gauntlets", ItemAmountStruct),
            ("Rune Gauntlets", ItemAmountStruct),
            ("Battle Gauntlets", ItemAmountStruct),
            ("Platinum Gauntlets", ItemAmountStruct),
            ("Mythril Gauntlets", ItemAmountStruct),
            ("Rare Gauntlets", ItemAmountStruct),
            ("Defenders", ItemAmountStruct),
            ("Garm's Fangs", ItemAmountStruct),
            ("Lizard Rippers", ItemAmountStruct),
            ("Crystal Cutters", ItemAmountStruct),
            ("Titan's Knuckles", ItemAmountStruct),
            ("Shining Talons", ItemAmountStruct),
            ("Omniweapon Fists", ItemAmountStruct),
            ("Therapeutic Slicers", ItemAmountStruct),
            ("Diabolic Slicers", ItemAmountStruct),
            ("Bryce's Claws", ItemAmountStruct),
            ("Kittlets", ItemAmountStruct),
            ("Danzo's Gauntlets", ItemAmountStruct),
            ("Seraphic Hearts", ItemAmountStruct),
            ("Destiny Breakers", ItemAmountStruct),
            ("Lefty &amp; Righty (kid)", ItemAmountStruct),
            ("Baronan Blades", ItemAmountStruct),
            ("Rune Dualblade", ItemAmountStruct),
            ("Platinum Dualblade", ItemAmountStruct),
            ("Mythril Dualblade", ItemAmountStruct),
            ("Rare Dualblade", ItemAmountStruct),
            ("Beastfang Blade", ItemAmountStruct),
            ("Twin Lancer", ItemAmountStruct),
            ("Aqua Limit", ItemAmountStruct),
            ("Voltekka", ItemAmountStruct),
            ("Rosary's Wrath", ItemAmountStruct),
            ("Bahamut's Tear", ItemAmountStruct),
            ("Sevenstar Dualblade", ItemAmountStruct),
            ("Pike Pike", ItemAmountStruct),
            ("Felling Wind", ItemAmountStruct),
            ("Brave Vesperia", ItemAmountStruct),
            ("Deathly Abyss", ItemAmountStruct),
            ("Throwing Knives", ItemAmountStruct),
            ("Steel Knives", ItemAmountStruct),
            ("Rune Knives", ItemAmountStruct),
            ("Battle Knives", ItemAmountStruct),
            ("Platinum Knives", ItemAmountStruct),
            ("Mythril Knives", ItemAmountStruct),
            ("Rare Knives", ItemAmountStruct),
            ("Fruit Knives", ItemAmountStruct),
            ("Bluesky Knives", ItemAmountStruct),
            ("Assassin's Daggers", ItemAmountStruct),
            ("Survival Knives", ItemAmountStruct),
            ("Impulse Blades", ItemAmountStruct),
            ("Prism Rainers", ItemAmountStruct),
            ("Keris Blades", ItemAmountStruct),
            ("Dragonbone Darts", ItemAmountStruct),
            ("Solbrights", ItemAmountStruct),
            ("O[]O[]-", ItemAmountStruct),
            ("Slivers of Dusk", ItemAmountStruct),
            ("Scars of Eternia", ItemAmountStruct),
            ("Innocent Shiners", ItemAmountStruct),
            ("Steel Bladerang", ItemAmountStruct),
            ("Rune Bladerang", ItemAmountStruct),
            ("Battle Bladerang", ItemAmountStruct),
            ("Platinum Bladerang", ItemAmountStruct),
            ("Mythril Bladerang", ItemAmountStruct),
            ("Rare Bladerang", ItemAmountStruct),
            ("Iron Bladerang", ItemAmountStruct),
            ("Feral Hunter", ItemAmountStruct),
            ("The Scrapper", ItemAmountStruct),
            ("The Illusionist", ItemAmountStruct),
            ("Third Supernova", ItemAmountStruct),
            ("The Undertaker", ItemAmountStruct),
            ("Dragon's Tooth", ItemAmountStruct),
            ("Elite Demonblade", ItemAmountStruct),
            ("The Peepinator", ItemAmountStruct),
            ("Eastern Wind", ItemAmountStruct),
            ("Tempest Bringer", ItemAmountStruct),
            ("Sword of Legendia", ItemAmountStruct),
            ("Steel Shotstaff", ItemAmountStruct),
            ("Rune Shotstaff", ItemAmountStruct),
            ("Battle Shotstaff", ItemAmountStruct),
            ("Platinum Shotstaff", ItemAmountStruct),
            ("Mythril Shotstaff", ItemAmountStruct),
            ("Rare Shotstaff", ItemAmountStruct),
            ("Frenzy Rod", ItemAmountStruct),
            ("Earthgale Staff", ItemAmountStruct),
            ("Splashwater Staff", ItemAmountStruct),
            ("Giant Hammer", ItemAmountStruct),
            ("Dreamer's Flange", ItemAmountStruct),
            ("Uroboros", ItemAmountStruct),
            ("Genius's Staff", ItemAmountStruct),
            ("Staff of Expiration", ItemAmountStruct),
            ("Looper Wooper", ItemAmountStruct),
            ("Ancient Khakkhara", ItemAmountStruct),
            ("Fandom's Light", ItemAmountStruct),
            ("Mythology Bearer", ItemAmountStruct),
            ("Short Rapier (kid)", ItemAmountStruct),
            ("Royal Rapier", ItemAmountStruct),
            ("Steel Saber", ItemAmountStruct),
            ("Fame and Faith", ItemAmountStruct),
            ("Kaiser Rapier", ItemAmountStruct),
            ("Symphonian Scepter", ItemAmountStruct),
            ("Rebirth Crusader", ItemAmountStruct),
            ("padding", c_uint8 * 18),  # 0x7E
            # total 0x90 bytes
        ]

    assert_struct_size(WeaponsStruct, 0x90)

    class ArmorsStruct(MarshalStructure):
        """Starts at offset 0xA891"""

        _fields_ = [
            ("Casual Parka", ItemAmountStruct),  # +0x0
            ("Casual Jacket", ItemAmountStruct),
            ("Haute Couture", ItemAmountStruct),
            ("Leather Guard", ItemAmountStruct),
            ("Iron Guard", ItemAmountStruct),
            ("Steel Guard", ItemAmountStruct),
            ("Rune Guard", ItemAmountStruct),
            ("Battle Guard", ItemAmountStruct),
            ("Platinum Guard", ItemAmountStruct),
            ("Mythril Guard", ItemAmountStruct),
            ("Rare Guard", ItemAmountStruct),
            ("Knight Armor", ItemAmountStruct),
            ("Ocean's Blue", ItemAmountStruct),
            ("Brave Force", ItemAmountStruct),
            ("Deep Crimson", ItemAmountStruct),
            ("Megingjord", ItemAmountStruct),
            ("Fortress Armor", ItemAmountStruct),
            ("Reflex", ItemAmountStruct),
            ("Last Crusader", ItemAmountStruct),
            ("Jade Vestments", ItemAmountStruct),
            ("Seablue Vestments", ItemAmountStruct),
            ("Abyssal Vestments", ItemAmountStruct),
            ("Mumbane", ItemAmountStruct),
            ("Jet Black Overalls", ItemAmountStruct),
            ("Ephinean Heartguard", ItemAmountStruct),
            ("Misty Blouse", ItemAmountStruct),
            ("Blouse", ItemAmountStruct),
            ("Silk Blouse", ItemAmountStruct),
            ("White Blouse", ItemAmountStruct),
            ("Rune Blouse", ItemAmountStruct),
            ("Black Blouse", ItemAmountStruct),
            ("Warlock's Garb", ItemAmountStruct),
            ("Mythril Blouse", ItemAmountStruct),
            ("Rare Blouse", ItemAmountStruct),
            ("Middy Blouse", ItemAmountStruct),
            ("Racy Corset", ItemAmountStruct),
            ("Cocktail Dress", ItemAmountStruct),
            ("Feathered Robe", ItemAmountStruct),
            ("Elder's Robe", ItemAmountStruct),
            ("Wildcat Wear", ItemAmountStruct),
            ("Pinafore Dress", ItemAmountStruct),
            ("Heavenly Garb", ItemAmountStruct),
            ("Silvered Vestments", ItemAmountStruct),
            ("Amber Vestments", ItemAmountStruct),
            ("Scarlet Vestments", ItemAmountStruct),
            ("Shrine Maiden's Garb", ItemAmountStruct),
            ("Jet Black Bodysuit", ItemAmountStruct),
            ("Fodrian Memory", ItemAmountStruct),
            ("Iron Tunic", ItemAmountStruct),
            ("Steel Tunic", ItemAmountStruct),
            ("Rune Tunic", ItemAmountStruct),
            ("Battle Tunic", ItemAmountStruct),
            ("Platinum Tunic", ItemAmountStruct),
            ("Mythril Tunic", ItemAmountStruct),
            ("Rare Tunic", ItemAmountStruct),
            ("Fatal Attraction", ItemAmountStruct),
            ("Vermilion Tunic", ItemAmountStruct),
            ("Turtlez Togz", ItemAmountStruct),
            ("Katz Klothez", ItemAmountStruct),
            ("padding", c_uint8 * 5),  # +0x3B
            # total 0x40 bytes
        ]

    assert_struct_size(ArmorsStruct, 0x40)

    class UniquesStruct(MarshalStructure):
        """Starts at offset 0xA8D1"""

        _fields_ = [
            ("Bronze Scabbard", ItemAmountStruct),  # +0x0
            ("Polished Bronze Scabbard", ItemAmountStruct),
            ("Iron Scabbard", ItemAmountStruct),
            ("Steel Scabbard", ItemAmountStruct),
            ("Hardened Steel Scabbard", ItemAmountStruct),
            ("Titanium Scabbard", ItemAmountStruct),
            ("Fine Titanium Scabbard", ItemAmountStruct),
            ("Silver Scabbard", ItemAmountStruct),
            ("Gold Scabbard", ItemAmountStruct),
            ("Platinum Scabbard", ItemAmountStruct),
            ("Hyper Scabbard", ItemAmountStruct),
            ("Rare Scabbard", ItemAmountStruct),
            ("Battle Scabbard", ItemAmountStruct),
            ("Grimm Scabbard", ItemAmountStruct),
            ("Fairy Scabbard", ItemAmountStruct),
            ("Anklet", ItemAmountStruct),
            ("Pretty Anklet", ItemAmountStruct),
            ("Cute Anklet", ItemAmountStruct),
            ("Floral Anklet", ItemAmountStruct),
            ("Fancy Floral Anklet", ItemAmountStruct),
            ("Titanium Anklet", ItemAmountStruct),
            ("Moon Anklet", ItemAmountStruct),
            ("Lunar Anklet", ItemAmountStruct),
            ("Star Anklet", ItemAmountStruct),
            ("Rune Anklet", ItemAmountStruct),
            ("Misty Anklet", ItemAmountStruct),
            ("Mythril Anklet", ItemAmountStruct),
            ("Grimm Anklet", ItemAmountStruct),
            ("Ancient Donut", ItemAmountStruct),
            ("Simple Frames", ItemAmountStruct),
            ("Plain Glasses", ItemAmountStruct),
            ("Silver Frames", ItemAmountStruct),
            ("Fancy Glasses", ItemAmountStruct),
            ("Gold Frames", ItemAmountStruct),
            ("Gold Glasses", ItemAmountStruct),
            ("Platinum Frames", ItemAmountStruct),
            ("Platinum Glasses", ItemAmountStruct),
            ("Goggles", ItemAmountStruct),
            ("Monocle", ItemAmountStruct),
            ("Scholar's Monocle", ItemAmountStruct),
            ("Nerdy Glasses", ItemAmountStruct),
            ("Ribbon", ItemAmountStruct),
            ("Pretty Ribbon", ItemAmountStruct),
            ("Lovely Ribbon", ItemAmountStruct),
            ("Red Ribbon", ItemAmountStruct),
            ("Freshblood Ribbon", ItemAmountStruct),
            ("Blue Ribbon", ItemAmountStruct),
            ("Orange Ribbon", ItemAmountStruct),
            ("Green Ribbon", ItemAmountStruct),
            ("Elemental Ribbon", ItemAmountStruct),
            ("Magical Ribbon", ItemAmountStruct),
            ("Ancient Cloth", ItemAmountStruct),
            ("Weird Ribbon", ItemAmountStruct),
            ("Jet Black Antennae", ItemAmountStruct),
            ("Natural Scent", ItemAmountStruct),
            ("Scarlet Aroma", ItemAmountStruct),
            ("Rose's Whisper", ItemAmountStruct),
            ("Mariner's Musk", ItemAmountStruct),
            ("Citrus Wind", ItemAmountStruct),
            ("Leafy Balm", ItemAmountStruct),
            ("Magic for Men", ItemAmountStruct),
            ("Mystical Allure", ItemAmountStruct),
            ("Tiger's Essence", ItemAmountStruct),
            ("Debonaire Dandy", ItemAmountStruct),
            ("Chivalrous Night", ItemAmountStruct),
            ("Eau de Peau", ItemAmountStruct),
            ("Long Scarf", ItemAmountStruct),
            ("Pretty Scarf", ItemAmountStruct),
            ("Beautiful Scarf", ItemAmountStruct),
            ("Red Scarf", ItemAmountStruct),
            ("Hot-Blooded Scarf", ItemAmountStruct),
            ("Blue Scarf", ItemAmountStruct),
            ("Orange Scarf", ItemAmountStruct),
            ("Mandarin Scarf", ItemAmountStruct),
            ("Green Scarf", ItemAmountStruct),
            ("Nature's Scarf", ItemAmountStruct),
            ("Magical Scarf", ItemAmountStruct),
            ("Fluffy Muffler", ItemAmountStruct),
            ("Fluffi Muffler", ItemAmountStruct),
            ("Fox...Scarf?", ItemAmountStruct),
            ("Royal Cloak", ItemAmountStruct),
            ("Elven Cloak", ItemAmountStruct),
            ("Undine Cloak", ItemAmountStruct),
            ("Gnome Cloak", ItemAmountStruct),
            ("Sylph Cloak", ItemAmountStruct),
            ("Efreet Cloak", ItemAmountStruct),
            ("padding", c_uint8 * 2),
            # total 0x58 bytes
        ]

    assert_struct_size(UniquesStruct, 0x58)

    _fields_ = [
        ("weapons", WeaponsStruct),  # +0x0
        ("armors", ArmorsStruct),  # +0x90
        ("uniques", UniquesStruct),  # +0xD0
        ("padding1", c_uint8 * 40),  # +0x128
        # total 0x150 bytes
    ]


assert_struct_size(EquipItemsArrayStruct, 0x150)


class GemsArrayStruct(MarshalStructure):
    """Starts at offset 0xA951"""

    _fields_ = [
        ("A-Gem", ItemAmountStruct),  # +0x0
        ("B-Gem", ItemAmountStruct),
        ("C-Gem", ItemAmountStruct),
        ("D-Gem", ItemAmountStruct),
        ("E-Gem", ItemAmountStruct),
        ("F-Gem", ItemAmountStruct),
        ("G-Gem", ItemAmountStruct),
        ("H-Gem", ItemAmountStruct),
        ("I-Gem", ItemAmountStruct),
        ("J-Gem", ItemAmountStruct),
        ("K-Gem", ItemAmountStruct),
        ("L-Gem", ItemAmountStruct),
        ("M-Gem", ItemAmountStruct),
        ("N-Gem", ItemAmountStruct),
        ("O-Gem", ItemAmountStruct),
        ("P-Gem", ItemAmountStruct),
        ("Q-Gem", ItemAmountStruct),
        ("R-Gem", ItemAmountStruct),
        ("S-Gem", ItemAmountStruct),
        # total 0x13 bytes
    ]


assert_struct_size(GemsArrayStruct, 0x13)


class CharmsArrayStruct(MarshalStructure):
    """Starts at offset 0xA964"""

    _fields_ = [
        ("Poison Charm", ItemAmountStruct),  # +0x0
        ("Paralysis Charm", ItemAmountStruct),
        ("Freeze Charm", ItemAmountStruct),
        ("Burn Charm", ItemAmountStruct),
        ("Stone Charm", ItemAmountStruct),
        ("Slow Charm", ItemAmountStruct),
        ("Seal Charm", ItemAmountStruct),
        ("Curse Charm", ItemAmountStruct),
        ("Weak Charm", ItemAmountStruct),
        ("Poison-Paralysis Charm", ItemAmountStruct),
        ("Poison-Freeze Charm", ItemAmountStruct),
        ("Poison-Burn Charm", ItemAmountStruct),
        ("Poison-Stone Charm", ItemAmountStruct),
        ("Poison-Slow Charm", ItemAmountStruct),
        ("Poison-Seal Charm", ItemAmountStruct),
        ("Poison-Curse Charm", ItemAmountStruct),
        ("Poison-Weak Charm", ItemAmountStruct),
        ("Paralysis-Freeze Charm", ItemAmountStruct),
        ("Paralysis-Burn Charm", ItemAmountStruct),
        ("Paralysis-Stone Charm", ItemAmountStruct),
        ("Paralysis-Slow Charm", ItemAmountStruct),
        ("Paralysis-Seal Charm", ItemAmountStruct),
        ("Paralysis-Curse Charm", ItemAmountStruct),
        ("Paralysis-Weak Charm", ItemAmountStruct),
        ("Freeze-Burn Charm", ItemAmountStruct),
        ("Freeze-Stone Charm", ItemAmountStruct),
        ("Freeze-Slow Charm", ItemAmountStruct),
        ("Freeze-Seal Charm", ItemAmountStruct),
        ("Freeze-Curse Charm", ItemAmountStruct),
        ("Freeze-Weak Charm", ItemAmountStruct),
        ("Burn-Stone Charm", ItemAmountStruct),
        ("Burn-Slow Charm", ItemAmountStruct),
        ("Burn-Seal Charm", ItemAmountStruct),
        ("Burn-Curse Charm", ItemAmountStruct),
        ("Burn-Weak Charm", ItemAmountStruct),
        ("Stone-Slow Charm", ItemAmountStruct),
        ("Stone-Seal Charm", ItemAmountStruct),
        ("Stone-Curse Charm", ItemAmountStruct),
        ("Stone-Weak Charm", ItemAmountStruct),
        ("Slow-Seal Charm", ItemAmountStruct),
        ("Slow-Curse Charm", ItemAmountStruct),
        ("Slow-Weak Charm", ItemAmountStruct),
        ("Seal-Curse Charm", ItemAmountStruct),
        ("Seal-Weak Charm", ItemAmountStruct),
        ("Curse-Weak Charm", ItemAmountStruct),
        # total 0x2D bytes
    ]


assert_struct_size(CharmsArrayStruct, 0x2D)


class ValuablesArrayStruct(MarshalStructure):
    """Starts at offset 0xA991"""

    _fields_ = [
        ("User's Guide", ItemAmountStruct),  # +0x0
        ("Collector's Book", ItemAmountStruct),
        ("Discovery Book", ItemAmountStruct),
        ("Enemy Book", ItemAmountStruct),
        ("World Map", ItemAmountStruct),
        ("Stamp Card Case", ItemAmountStruct),
        ("Manual Manual", ItemAmountStruct),
        ("Eleth Mixer", ItemAmountStruct),
        ("Soul Orb", ItemAmountStruct),
        ("Glassphere", ItemAmountStruct),
        ("Trash", ItemAmountStruct),
        ("Arithmos Core", ItemAmountStruct),
        ("Plucked Flower", ItemAmountStruct),
        ("Richard's Ring", ItemAmountStruct),
        ("Letter from Mom", ItemAmountStruct),
        ("Fortress Key", ItemAmountStruct),
        ("Pressed Sopheria", ItemAmountStruct),
        ("Letter to the President", ItemAmountStruct),
        ("Good-Luck Charm", ItemAmountStruct),
        ("Rockgagong Flute", ItemAmountStruct),
        ("Pascal's Diagram", ItemAmountStruct),
        ("ID Card", ItemAmountStruct),
        ("Spy's Letter", ItemAmountStruct),
        ("Old Military Credentials", ItemAmountStruct),
        ("Elevator Key", ItemAmountStruct),
        ("Security Pass", ItemAmountStruct),
        ("Chancellor's Letter", ItemAmountStruct),
        ("Archive of Wisdom Key", ItemAmountStruct),
        ("Pigeon Communicator", ItemAmountStruct),
        ("Derris Bit", ItemAmountStruct),
        ("Derris Rings", ItemAmountStruct),
        ("Deleted Item", ItemAmountStruct),
        ("Sopheria Seeds", ItemAmountStruct),
        ("Night Lily Seeds", ItemAmountStruct),
        ("Canola Seeds", ItemAmountStruct),
        ("Amaryllis Seeds", ItemAmountStruct),
        ("Gerbera Seeds", ItemAmountStruct),
        ("Lassamble Seeds", ItemAmountStruct),
        ("Daphne Seeds", ItemAmountStruct),
        ("Niferum Seeds", ItemAmountStruct),
        ("Bloody Rose Seeds", ItemAmountStruct),
        ("Jack-in-the-Pulpit Seeds", ItemAmountStruct),
        ("Nameless Flower Seeds", ItemAmountStruct),
        ("Cat Pine Seeds", ItemAmountStruct),
        ("Turtlez Tot's Note", ItemAmountStruct),
        ("Katz Plushie", ItemAmountStruct),
        ("Estelle Plushie", ItemAmountStruct),
        ("Prince Plushie", ItemAmountStruct),
        ("Ba'ul Plushie", ItemAmountStruct),
        ("Bush Baby Plushie", ItemAmountStruct),
        ("Imp Plushie", ItemAmountStruct),
        ("Noko Plushie", ItemAmountStruct),
        ("Moji-kun Plushie", ItemAmountStruct),
        ("Mizu-chan Plushie", ItemAmountStruct),
        ("Lara's Medal", ItemAmountStruct),
        ("Best Princess Stories", ItemAmountStruct),
        ("Victor's Badge", ItemAmountStruct),
        ("Conqueror's Badge", ItemAmountStruct),
        ("Amarcian Key", ItemAmountStruct),
        ("Memory Core", ItemAmountStruct),
        ("Requiem", ItemAmountStruct),
        ("Lost Anklet", ItemAmountStruct),
        ("Hero Staff", ItemAmountStruct),
        ("Argo Iris", ItemAmountStruct),
        ("Turtlez Flute", ItemAmountStruct),
        ("Katz Dekoder", ItemAmountStruct),
        ("Glonandrake's Cryas", ItemAmountStruct),
        ("Duplewyrm's Cryas", ItemAmountStruct),
        ("Forbrawyvern's Cryas", ItemAmountStruct),
        ("Letter from Richard", ItemAmountStruct),
        ("Gas Control Lever", ItemAmountStruct),
        ("Memory Data", ItemAmountStruct),
        ("Red Liquid", ItemAmountStruct),
        ("Purple Liquid", ItemAmountStruct),
        ("Yellow Liquid", ItemAmountStruct),
        ("Green Liquid", ItemAmountStruct),
        ("Grey Liquid", ItemAmountStruct),
        ("Book of Perfection", ItemAmountStruct),
        ("Book of Maintenance", ItemAmountStruct),
        ("Book of Wealth", ItemAmountStruct),
        ("Book of Dissolution", ItemAmountStruct),
        ("Book of Talent", ItemAmountStruct),
        ("Book of Precedence", ItemAmountStruct),
        ("Book of Suppression", ItemAmountStruct),
        ("Book of Sustenance", ItemAmountStruct),
        ("Book of Restraint", ItemAmountStruct),
        ("Book of Potential", ItemAmountStruct),
        ("Book of Preemption", ItemAmountStruct),
        ("Book of Gathering", ItemAmountStruct),
        ("Book of Acquisition", ItemAmountStruct),
        ("Book of Duplication", ItemAmountStruct),
        ("Book of Swiftness", ItemAmountStruct),
        ("Book of Metabolism", ItemAmountStruct),
        ("Book of Finesse", ItemAmountStruct),
        ("Book of Satiation", ItemAmountStruct),
        ("Book of Serendipity", ItemAmountStruct),
        ("Book of Cuisine", ItemAmountStruct),
        ("Book of Valor", ItemAmountStruct),
        ("Book of Holy Water", ItemAmountStruct),
        ("Book of Solitude", ItemAmountStruct),
        ("Book of Deduction", ItemAmountStruct),
        ("Book of Exchanging", ItemAmountStruct),
        ("Book of Enthusiasm", ItemAmountStruct),
        ("Book of Fortune", ItemAmountStruct),
        ("Book of Passion", ItemAmountStruct),
        ("Book of Striking", ItemAmountStruct),
        ("Book of Restriction", ItemAmountStruct),
        ("Book of Growth", ItemAmountStruct),
        ("Book of Expansion", ItemAmountStruct),
        ("Book of Smithery", ItemAmountStruct),
        ("Book of Audacity", ItemAmountStruct),
        ("Book of Friendship", ItemAmountStruct),
        ("Book of Fortitude", ItemAmountStruct),
        ("Book of Partnership", ItemAmountStruct),
        ("Book of Glory", ItemAmountStruct),
        ("Book of Awakening", ItemAmountStruct),
        ("Book of Frugality", ItemAmountStruct),
        ("Magic Carta No. 1", ItemAmountStruct),
        ("Magic Carta No. 2", ItemAmountStruct),
        ("Magic Carta No. 3", ItemAmountStruct),
        ("Magic Carta No. 4", ItemAmountStruct),
        ("Magic Carta No. 5", ItemAmountStruct),
        ("Magic Carta No. 6", ItemAmountStruct),
        ("Magic Carta No. 7", ItemAmountStruct),
        ("Magic Carta No. 8", ItemAmountStruct),
        ("Magic Carta No. 9", ItemAmountStruct),
        ("Magic Carta No. 10", ItemAmountStruct),
        ("Magic Carta No. 11", ItemAmountStruct),
        ("Magic Carta No. 12", ItemAmountStruct),
        ("Magic Carta No. 13", ItemAmountStruct),
        ("Magic Carta No. 14", ItemAmountStruct),
        ("Magic Carta No. 15", ItemAmountStruct),
        ("Magic Carta No. 16", ItemAmountStruct),
        ("Magic Carta No. 17", ItemAmountStruct),
        ("Magic Carta No. 18", ItemAmountStruct),
        ("Magic Carta No. 19", ItemAmountStruct),
        ("Magic Carta No. 20", ItemAmountStruct),
        ("Magic Carta No. 21", ItemAmountStruct),
        ("Magic Carta No. 22", ItemAmountStruct),
        ("Magic Carta No. 23", ItemAmountStruct),
        ("Magic Carta No. 24", ItemAmountStruct),
        ("Magic Carta No. 25", ItemAmountStruct),
        ("Magic Carta No. 26", ItemAmountStruct),
        ("Magic Carta No. 27", ItemAmountStruct),
        ("Magic Carta No. 28", ItemAmountStruct),
        ("Magic Carta No. 29", ItemAmountStruct),
        ("Magic Carta No. 30", ItemAmountStruct),
        ("Magic Carta No. 31", ItemAmountStruct),
        ("Magic Carta No. 32", ItemAmountStruct),
        ("Magic Carta No. 33", ItemAmountStruct),
        ("Magic Carta No. 34", ItemAmountStruct),
        ("Magic Carta No. 35", ItemAmountStruct),
        ("Magic Carta No. 36", ItemAmountStruct),
        ("Magic Carta No. 37", ItemAmountStruct),
        ("Magic Carta No. 38", ItemAmountStruct),
        ("Magic Carta No. 39", ItemAmountStruct),
        ("Magic Carta No. 40", ItemAmountStruct),
        ("Magic Carta No. 41", ItemAmountStruct),
        ("Magic Carta No. 42", ItemAmountStruct),
        ("Magic Carta No. 43", ItemAmountStruct),
        ("Magic Carta No. 44", ItemAmountStruct),
        ("Magic Carta No. 45", ItemAmountStruct),
        ("Magic Carta No. 46", ItemAmountStruct),
        ("Magic Carta No. 47", ItemAmountStruct),
        ("Magic Carta No. 48", ItemAmountStruct),
        ("Magic Carta No. 49", ItemAmountStruct),
        ("Magic Carta No. 50", ItemAmountStruct),
        ("Magic Carta No. 51", ItemAmountStruct),
        ("Magic Carta No. 52", ItemAmountStruct),
        ("Magic Carta No. 53", ItemAmountStruct),
        ("Magic Carta No. 54", ItemAmountStruct),
        ("Magic Carta No. 55", ItemAmountStruct),
        ("Magic Carta No. 56", ItemAmountStruct),
        ("Magic Carta No. 57", ItemAmountStruct),
        ("Magic Carta No. 58", ItemAmountStruct),
        ("Magic Carta No. 59", ItemAmountStruct),
        ("Magic Carta No. 60", ItemAmountStruct),
        ("Magic Carta No. 61", ItemAmountStruct),
        ("Magic Carta No. 62", ItemAmountStruct),
        ("Magic Carta No. 63", ItemAmountStruct),
        ("Magic Carta No. 64", ItemAmountStruct),
        ("Magic Carta No. 65", ItemAmountStruct),
        ("Magic Carta No. 66", ItemAmountStruct),
        ("Magic Carta No. 67", ItemAmountStruct),
        ("Magic Carta No. 68", ItemAmountStruct),
        ("Magic Carta No. 69", ItemAmountStruct),
        ("Magic Carta No. 70", ItemAmountStruct),
        ("Magic Carta No. 71", ItemAmountStruct),
        ("Magic Carta No. 72", ItemAmountStruct),
        ("Magic Carta No. 73", ItemAmountStruct),
        ("Magic Carta No. 74", ItemAmountStruct),
        ("Magic Carta No. 75", ItemAmountStruct),
        ("Magic Carta No. 76", ItemAmountStruct),
        ("Magic Carta No. 77", ItemAmountStruct),
        ("Magic Carta No. 78", ItemAmountStruct),
        ("Magic Carta No. 79", ItemAmountStruct),
        ("Magic Carta No. 80", ItemAmountStruct),
        ("Magic Carta No. 81", ItemAmountStruct),
        ("Magic Carta No. 82", ItemAmountStruct),
        ("Magic Carta No. 83", ItemAmountStruct),
        ("Magic Carta No. 84", ItemAmountStruct),
        ("Magic Carta No. 85", ItemAmountStruct),
        ("Magic Carta No. 86", ItemAmountStruct),
        ("Magic Carta No. 87", ItemAmountStruct),
        ("Magic Carta No. 88", ItemAmountStruct),
        ("Magic Carta No. 89", ItemAmountStruct),
        ("Magic Carta No. 90", ItemAmountStruct),
        ("Assorted Flowers", ItemAmountStruct),
        ("Anonymous Letter", ItemAmountStruct),
        ("Beloved Handkerchief", ItemAmountStruct),
        ("Model Ship", ItemAmountStruct),
        ("Royal Knights' Documents", ItemAmountStruct),
        ("Windor's Military History", ItemAmountStruct),
        ("Windor Crest", ItemAmountStruct),
        ("Tuning Fork", ItemAmountStruct),
        ("Green Cryas", ItemAmountStruct),
        ("Wallbridge Evidence", ItemAmountStruct),
        ("Businezz Application", ItemAmountStruct),
        ("Book of Rare Creatures", ItemAmountStruct),
        ("Trade Permit", ItemAmountStruct),
        ("Sunken Cargo", ItemAmountStruct),
        ("Abandoned Cargo", ItemAmountStruct),
        ("Blue Cryas", ItemAmountStruct),
        ("Investigation Report", ItemAmountStruct),
        ("Treasured Picture", ItemAmountStruct),
        ("Proof of Another World", ItemAmountStruct),
        ("Polishing Tools", ItemAmountStruct),
        ("Cherished Locket", ItemAmountStruct),
        ("Hand-Drawn Map", ItemAmountStruct),
        ("Seablue Statue", ItemAmountStruct),
        ("Daily Medicine", ItemAmountStruct),
        ("Spoon", ItemAmountStruct),
        ("Spade", ItemAmountStruct),
        ("Drill", ItemAmountStruct),
        ("Raw Materials", ItemAmountStruct),
        ("Rockgagong Fur", ItemAmountStruct),
        ("Strahta Ratchet", ItemAmountStruct),
        ("Evidence of Espionage", ItemAmountStruct),
        ("Research Sample", ItemAmountStruct),
        ("Gauss's Seal", ItemAmountStruct),
        ("Kurt's Pendant", ItemAmountStruct),
        ("Replacement Part", ItemAmountStruct),
        ("Drive Unit", ItemAmountStruct),
        ("Broken Brooch", ItemAmountStruct),
        ("Data Recorder", ItemAmountStruct),
        ("Winner's Trophy", ItemAmountStruct),
        ("Liquisilk Fabric", ItemAmountStruct),
        ("Pearl Windthread", ItemAmountStruct),
        ("Shark Fin", ItemAmountStruct),
        ("padding1", c_uint8 * 6),  # +0xF9
        # total 0xFF bytes
    ]


assert_struct_size(ValuablesArrayStruct, 0xFF)


class AllItemsAmountArray(MarshalStructure):
    """Starts at offset 0xA634"""

    _fields_ = [
        ("unknown_items", UnknownItemsArrayStruct),  # +0x0
        ("consumables", ConsumablesItemsArrayStruct),  # +0xD
        ("dishes", DishesArrayStruct),  # +0x31
        ("materials", MaterialsArrayStruct),  # +0xAD
        ("cashables", CashablesArrayStruct),  # +0x128
        ("ingredients", IngredientsArrayStruct),  # +0x16A
        ("unknown_items2", c_uint8 * 51),  # +0x19A
        ("equip_items", EquipItemsArrayStruct),  # +0x1CD
        ("gems", GemsArrayStruct),  # +0x31D
        ("charms", CharmsArrayStruct),  # +0x330
        ("valuables", ValuablesArrayStruct),  # +0x35E
        # total 0x45C bytes
    ]


assert_struct_size(AllItemsAmountArray, 0x45C)


class CollectorStateDataStruct(MarshalStructure):
    class CollectorBookItems(MarshalStructure):
        """Starts at offset 0xAABC"""

        _fields_ = [
            ("items", c_uint8 * 5)  # + 0x0
            # total 0x5
        ]

    assert_struct_size(CollectorBookItems, 0x5)

    class CollectorBookDishes(MarshalStructure):
        """Starts at offset 0xAAC1"""

        _fields_ = [
            ("dishes", c_uint8 * 14)  # + 0x0
            # total 0xE
        ]

    assert_struct_size(CollectorBookDishes, 0xE)

    class CollectorBookMaterials(MarshalStructure):
        """Starts at offset 0xAAD4"""

        _fields_ = [
            ("materials", c_uint8 * 9 * 4)  # + 0x0
            # total 0x24
        ]

    assert_struct_size(CollectorBookMaterials, 0x24)

    class CollectorBookWeapons(MarshalStructure):
        """Starts at offset 0xAAFC"""

        _fields_ = [
            ("weapon", c_uint8 * 4 * 4)  # + 0x0
            # total 0x10
        ]

    assert_struct_size(CollectorBookWeapons, 0x10)

    class CollectorBookArmors(MarshalStructure):
        """Starts at offset 0xAB14"""

        _fields_ = [
            ("armor", c_uint8 * 8)  # + 0x0
            # total 0x8
        ]

    assert_struct_size(CollectorBookArmors, 0x8)

    class CollectorBookUniqueEquipment(MarshalStructure):
        """Starts at offset 0xAB1C"""

        _fields_ = [
            ("unique equip", c_uint8 * 12)  # + 0x0
            # total 0xC
        ]

    assert_struct_size(CollectorBookUniqueEquipment, 0xC)

    class CollectorBookGems(MarshalStructure):
        """Starts at offset 0xAB2C"""

        _fields_ = [
            ("gem", c_uint8 * 3 * 4)  # + 0x0
            # total 0xC
        ]

    assert_struct_size(CollectorBookGems, 0xC)

    class CollectorBookValuables(MarshalStructure):
        """Starts at offset 0xAB3C"""

        _fields_ = [
            ("valuable", c_uint8 * 8 * 4)  # + 0x0
            # total 0x20
        ]

    assert_struct_size(CollectorBookValuables, 0x20)

    class UnknownBitmapAt_0xAB64(MarshalStructure):
        """Starts at offset 0xAB64"""

        _fields_ = [
            ("unknown", c_uint8 * 5 * 4)  # + 0x0
            # total 0x20
        ]

    assert_struct_size(UnknownBitmapAt_0xAB64, 0x14)

    class UnknownBitmapAt_0xAB7C(MarshalStructure):
        """Starts at offset 0xAB7C"""

        _fields_ = [
            ("unknown", c_uint8 * 4)  # + 0x0
            # total 0x4
        ]

    assert_struct_size(UnknownBitmapAt_0xAB7C, 0x4)

    class UnknownBitmapAt_0xAB88(MarshalStructure):
        """Starts at offset 0xAB88"""

        _fields_ = [
            ("unknown", c_uint8 * 3 * 4)  # + 0x0
            # total 0xC
        ]

    assert_struct_size(UnknownBitmapAt_0xAB88, 0xC)

    """Starts at offset 0xAABC"""
    _fields_ = [
        ("items", CollectorBookItems),  # +0x0
        ("dishes", CollectorBookDishes),  # +0x5
        ("align0", c_uint8),  # +0x13 - Align to 4-byte boundary
        ("padding0", c_uint32),  # +0x14
        ("materials", CollectorBookMaterials),  # +0x18
        ("padding1", c_uint32),  # +0x3C
        ("weapons", CollectorBookWeapons),  # +0x40
        ("padding2", c_uint32 * 2),  # +0x54
        ("armors", CollectorBookArmors),  # +0x58
        ("unique_equips", CollectorBookUniqueEquipment),  # +0x60
        ("padding3", c_uint32),  # +0x6C
        ("gems", CollectorBookGems),  # +0x70
        ("padding4", c_uint32),  # +0x7C
        ("valuables", CollectorBookValuables),  # +0x80
        ("padding5", c_uint32 * 2),  # +0xA0
        ("unknown_bitmap_at_0xAB64", UnknownBitmapAt_0xAB64),  # +0xA8
        ("padding6", c_uint32),  # +0xBC
        ("unknown_bitmap_at_0xAB7C", UnknownBitmapAt_0xAB7C),  # +0xC0
        ("padding7", c_uint32 * 2),  # +0xC4
        ("unknown_bitmap_at0xAB88", UnknownBitmapAt_0xAB88),  # +0xCC
        # total 0xD8 bytes
    ]


assert_struct_size(CollectorStateDataStruct, 0xD8)


class StampsReceivedStruct(MarshalStructure):
    """Starts at offset 0xABB8"""

    _fields_ = [
        ("stamps", c_uint16),  # +0x0
        # total 0x2 bytes
    ]


assert_struct_size(StampsReceivedStruct, 0x2)


class NewItemStruct(MarshalStructure):
    """Starts at offset 0xABBC"""

    _fields_ = [
        ("item_type", c_uint8 * 2),  # +0x0
        ("item_id", c_uint16),  # +0x2
        # total 0x4 bytes
    ]


assert_struct_size(NewItemStruct, 0x4)


class NewItemArray(MarshalStructure):
    """Starts at offset 0xABBE"""

    _fields_ = [
        ("new_items", NewItemStruct * 14),  # +0x0
        # total 0x38 bytes
    ]


assert_struct_size(NewItemArray, 0x38)


class ElethDataStruct(MarshalStructure):
    """Starts at offset 0xABF8"""

    _fields_ = [
        ("curr_eleth", c_uint16),  # +0x0
        ("max_eleth", c_uint16),  # +0x2
        ("items_ids_in slots", c_uint16 * 16),  # +0x2
        # total 0x24 bytes
    ]


assert_struct_size(ElethDataStruct, 0x24)


class ElethMixerDataStruct(MarshalStructure):
    """Starts at offset 0xAC1C"""

    _fields_ = [
        ("mixer_slots", c_uint8),  # +0x0
        # total 0x1 bytes
    ]


assert_struct_size(ElethMixerDataStruct, 0x1)

# Encounter count is located at 0xAC20 - 4 bytes
# Gold amount is located at 0x76D4 - 4 bytes
# Menu Play time amount is located at 0x76D8 - 4 bytes quantized as 1/60 of a second segments
#   i.e a value of 60 = 1 second, a value of 3600 = 1 minute
# Current Eleth amount is located at 0xABF8 - 2 bytes
# Max Eleth amount is located at 0xABFA - 2 bytes
# Total Encounter record is at 0xB9B0 - 4 bytes
# Eleth consumed record is located at 0xB9DC - 4 bytes
# Total Play time record is located at 0xB9E0 - 4 bytes quantized as 1/60 of a second segments
# Chest opened count is located at 0xB9E4 - 2 bytes
# People spoken to is located at 0xB9E6 - 2 bytes
# best combo record is located at 0xB9E8 - 2 bytes
# max hit is located at 0xAC40 - 2 bytes


class EncounterDataStruct(MarshalStructure):
    """Starts at offset 0xAC20"""

    _fields_ = [
        ("encounter_count", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(EncounterDataStruct, 0x4)


class OtherGameData(MarshalStructure):
    """Starts at offset 0xAC24"""

    _fields_ = [
        ("game_data_values", c_uint32 * 7),  # +0x0
        # total 0x1C bytes
    ]


assert_struct_size(OtherGameData, 0x1C)


class MaxHitCountStruct(MarshalStructure):
    """Starts at offset 0xAC40"""

    _fields_ = [
        ("max_hit_count", c_uint16),  # +0x0
        # total 0x2 bytes
    ]


assert_struct_size(MaxHitCountStruct, 0x2)


class GradeShopDataStruct(MarshalStructure):
    """Starts at offset 0xAC44
    Stored as a bitmap
    """

    _fields_ = [
        ("inherit_titles", c_uint8, 1),  # +0x0 bit 0
        ("inherit_skills", c_uint8, 1),  # +0x0 bit 1
        ("inherit_eleth_mixer", c_uint8, 1),  # +0x0 bit 2
        ("inherit_gald", c_uint8, 1),  # +0x0 bit 3
        ("inherit_stampes", c_uint8, 1),  # +0x0 bit 4
        ("inherit_arte_usage", c_uint8, 1),  # +0x0 bit 5
        ("inherit_books", c_uint8, 1),  # +0x0 bit 6
        ("inherit_battle_items", c_uint8, 1),  # +0x0 bit 7
        ("inherit_shards", c_uint8, 1),  # +0x1 bit 0
        ("inherit_herb_bonuses", c_uint8, 1),  # +0x1 bit 1
        ("trader_exp_for_gald", c_uint8, 1),  # +0x1 bit 2
        ("double_experience", c_uint8, 1),  # +0x1 bit 3
        ("experience_5x", c_uint8, 1),  # +0x1 bit 4
        ("half_experience", c_uint8, 1),  # +0x1 bit 5
        ("double_sp", c_uint8, 1),  # +0x1 bit 6
        ("triple_sp", c_uint8, 1),  # +0x1 bit 7
        ("mastery_bonus", c_uint8, 1),  # +0x2 bit 0
        ("double_item_drops", c_uint8, 1),  # +0x2 bit 1
        ("dualize_discount", c_uint8, 1),  # +0x2 bit 2
        ("upgrade_eleth_mixer", c_uint8, 1),  # +0x2 bit 3
        ("expand_inventory", c_uint8, 1),  # +0x2 bit 4
        ("maximum_speed", c_uint8, 1),  # +0x2 bit 5
        ("chain_capacity_plus_1", c_uint8, 1),  # +0x2 bit 6
        ("chain_capacity_plus_2", c_uint8, 1),  # +0x2 bit 7
        ("double_critical", c_uint8, 1),  # +0x3 bit 0
        ("double_damage", c_uint8, 1),  # +0x3 bit 1
        ("damage_5x", c_uint8, 1),  # +0x3 bit 2
        ("double_gald", c_uint8, 1),  # +0x3 bit 3
        ("unlock_qualities", c_uint8, 1),  # +0x3 bit 4
        ("maximum_eleth_plus_500", c_uint8, 1),  # +0x3 bit 5
        ("maximum_hp_plus_1000", c_uint8, 1),  # +0x3 bit 6
        ("skip_childhood", c_uint8, 1),  # +0x3 bit 7
        ("inherit_carta_cards", c_uint8, 1),  # +0x4 bit 0
        ("half_shop_prices", c_uint8, 1),  # +0x4 bit 1
        ("padding1", c_uint8 * 3),  # +0x5
        # total 0x8 bytes
    ]


assert_struct_size(GradeShopDataStruct, 0x8)


class ShopUnknownStructArrayAt_0xAC4C(MarshalStructure):
    class ShopUnknownStructAt_0xAC4C(MarshalStructure):
        """
        Starts at offset 0xAC4C
        ShopUnknownStructArrayAt_0xAC4C
        Specifically the 4-bytes at offset +0x4 and +0x6
        needs to be endian swapped, otherwise the game
        crashes when accessing a shop
        """

        _fields_ = [
            ("unknown_marker1", c_uint32),  # +0x0
            ("unknown_count", c_uint16),  # +0x4
            ("unknown_value1", c_uint16),  # +0x6
            ("unknown_value2", c_uint8 * 8),  # +0x8
            ("unknown_value3", c_uint8 * 2),  # +0x10
            ("unknown_value4", c_uint8 * 2),  # +0x12
            ("unknown_value5", c_uint8 * 2),  # +0x14
            ("unknown_value6", c_uint8 * 2),  # +0x16
            ("unknown_id1", c_uint8 * 2),  # +0x18
            ("unknown_id2", c_uint8 * 2),  # +0x1A
            ("unknown_bytes", c_uint8 * 4),  # +0x1C
            ("unknown_bytes", c_uint8 * 4),  # +0x20
            ("item_id1?", c_uint16),  # +0x24
            ("item_id2?", c_uint16),  # +0x26
            # total 0x28 bytes
        ]

    assert_struct_size(ShopUnknownStructAt_0xAC4C, 0x28)

    """Starts at offset 0xAC4C"""
    _fields_ = [
        ("shops", ShopUnknownStructAt_0xAC4C * 13),  # +0x0
        # total 0x208 bytes
    ]


assert_struct_size(ShopUnknownStructArrayAt_0xAC4C, 0x208)


class UnknownShortsAt_0xAE7C(MarshalStructure):
    """Starts at offset 0xAE7C"""

    _fields_ = [
        ("unknown_short", c_uint16 * 56),  # +0x0
        # total 0x70 bytes
    ]


assert_struct_size(UnknownShortsAt_0xAE7C, 0x70)


class DiscoveriesBitfieldDataStruct(MarshalStructure):
    """Starts at offset 0xAF1C"""

    _fields_ = [
        ("discoveries", c_uint32 * 3)  # + 0x0
        # total 0xC
    ]


assert_struct_size(DiscoveriesBitfieldDataStruct, 0xC)


class UnknownBitfieldAt_0xAF2C(MarshalStructure):
    """Starts at offset 0xAF2C"""

    _fields_ = [
        ("unknown", c_uint32 * 4)  # + 0x0
        # total 0x10
    ]


assert_struct_size(UnknownBitfieldAt_0xAF2C, 0x10)


class UnknownBitfieldAt_0xAF4C(MarshalStructure):
    """Starts at offset 0xAF4C"""

    _fields_ = [
        ("unknown", c_uint32 * 2)  # + 0x0
        # total 0x08
    ]


assert_struct_size(UnknownBitfieldAt_0xAF4C, 0x8)


class EnemyDataArray(MarshalStructure):
    """Starts at offset 0xAF54"""

    class EnemyDataBits(MarshalStructure):
        """Bitfield for enemy data"""

        _fields_ = [
            ("seen", c_uint8, 1),
            ("blank_star?", c_uint8, 1),
            ("unknown_bits1", c_uint8, 1),
            ("unknown_bits2", c_uint8, 1),
            ("always_0_bit", c_uint8, 1),
            ("full_star", c_uint8, 1),
            ("padding_bits", c_uint8, 2),
            # total 0x1
        ]

    _fields_ = [
        ("enemies", EnemyDataBits * 330)  # + 0x0
        # total 0x14A
    ]


assert_struct_size(EnemyDataArray, 0x14A)


class UnknownShortsAt_0xB0D8(MarshalStructure):
    """Starts at offset 0xB0D8"""

    _fields_ = [
        ("unknown", c_uint16 * 328)  # + 0x0
        # total 0x290
    ]


assert_struct_size(UnknownShortsAt_0xB0D8, 0x290)


class MoreUnknownShortsAt_0xB3D8(MarshalStructure):
    """Starts at offset 0xB3D8"""

    _fields_ = [
        ("unknown", c_uint16 * 328)  # + 0x0
        # total 0x290
    ]


assert_struct_size(MoreUnknownShortsAt_0xB3D8, 0x290)


class GradeBonusDataStruct(MarshalStructure):
    """Starts at offset 0xB8B0"""

    _fields_ = [
        ("clear_bonus", c_uint16),  # + 0x0
        ("title_bonus", c_uint16),  # + 0x2
        ("skill_bonus", c_uint16),  # + 0x4
        ("arte_usage_bonus", c_uint16),  # + 0x6
        ("book_completion_bonus", c_uint16),  # + 0x8
        ("side_quest_bonus", c_uint16),  # + 0xA
        ("combo_bonus", c_uint16),  # + 0xC
        ("technical_bonus", c_uint16),  # + 0xE
        ("ex_dungeon_bonus", c_uint16),  # + 0x10
        ("speed_bonus", c_uint16),  # + 0x12
        ("unyielding_bonus", c_uint16),  # + 0x14
        ("short_padding", c_uint16),  # + 0x16 <-- The unyielding bonus might be an c_uint32, but I am not sure
        # So instead a guess is being made that there is 2 bytes padding afterwards
        ("exterminator_bonus", c_uint16),  # + 0x18
        ("save_the_gels_bonus", c_uint16),  # + 0x1A
        ("enhancement_bonus", c_uint16),  # + 0x1C
    ]


assert_struct_size(GradeBonusDataStruct, 0x1E)


class UnknownStructArrayAt_0xB8D0(MarshalStructure):
    """Starts at offset 0xB8D0"""

    class UnknownStructAt_0xB8D0(MarshalStructure):
        _fields_ = [
            ("unknown_int1", c_uint32),  # +0x0
            ("unknown_value", c_uint8 * 2),  # +0x4
            ("padding1", c_uint8 * 10),  # +0x6
            # total 0x10 bytes
        ]

    _fields_ = [
        ("unknown_struct", UnknownStructAt_0xB8D0 * 12),  # +0x0
        # total 0xC0 bytes
    ]


assert_struct_size(UnknownStructArrayAt_0xB8D0, 0xC0)


class RecordDataUnknownStruct(MarshalStructure):
    """Starts at offset 0xB994"""

    _fields_ = [
        ("unknown_int1", c_uint32),  # +0x0
        ("record_id?", c_uint16 * 2),  # +0x4
        ("unknown_record_bytes", c_uint8 * 20),  # +0x8
        # total 0x1C bytes
    ]


assert_struct_size(RecordDataUnknownStruct, 0x1C)


class RecordDataStruct(MarshalStructure):
    """Starts at offset 0xB9B0"""

    _fields_ = [
        ("total_encounters", c_uint32),  # +0x0
        ("best_equip_resell", c_uint32),  # +0x4
        ("distance_traveled_kilometer", c_float),  # +0x8
        ("distance_traveled_micro_kilometer", c_float),  # +0xC
        ("curr_gald", c_uint32),  # +0x10
        ("most_gald_held", c_uint32),  # +0x14
        ("total_gald_spent", c_uint32),  # +0x18
        ("unknown_ints?", c_uint32 * 4),  # +0x1C
        ("eleth_consumed", c_uint32),  # +0x2C
        ("playtime", c_uint32),  # +0x30
        ("chest_opened", c_uint16),  # +0x34
        ("people_spoken_to", c_uint16),  # +0x36
        ("best_combo", c_uint16),  # +0x38
        ("padding1", c_uint16),  # +0x3A
        # total 0x3C bytes
    ]


assert_struct_size(RecordDataStruct, 0x3C)


class BattlePlaytimeGameDataStructAt_0xBB70(MarshalStructure):
    """Starts at offset 0xBB70"""

    _fields_ = [
        ("unknown_id1", c_uint8 * 2),  # +0x0
        ("unknown_short1", c_uint16),  # +0x2
        ("unknown_id2", c_uint8 * 2),  # +0x4
        ("unknown_short2", c_uint16),  # +0x6
        ("unknown_int1", c_uint32),  # +0x8
        ("unknown_bitmaps", c_uint32 * 6),  # +0xC
        ("time_value_1_60th?", c_uint32),  # +0x24
        ("padding", c_uint32),  # +0x28
        ("battle_playtime", c_uint32),  # +0x2C
        # total 0x30 bytes
    ]


assert_struct_size(BattlePlaytimeGameDataStructAt_0xBB70, 0x30)


class UnknownIntAt_0xBBB0(MarshalStructure):
    """Starts at offset 0xBBB0"""

    _fields_ = [
        ("unknown_int", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(UnknownIntAt_0xBBB0, 0x4)


class UnknownStructAt_0xBBBC(MarshalStructure):
    """Starts at offset 0xBBBC"""

    _fields_ = [
        ("unknown_id", c_uint8 * 2),  # +0x0
        ("unknown_shorts", c_uint16 * 13),  # +0x2
        ("unknown_int", c_uint32),  # +0x1C
        # total 0x20 bytes
    ]


assert_struct_size(UnknownStructAt_0xBBBC, 0x20)


class UnknownIntsAt_0xBC1C(MarshalStructure):
    """Starts at offset 0xBC1C"""

    _fields_ = [
        ("unknown_ints", c_uint32 * 8),  # +0x0
        # total 0x20 bytes
    ]


assert_struct_size(UnknownIntsAt_0xBC1C, 0x20)


class UnknownIntsAt_0xBC60(MarshalStructure):
    """Starts at offset 0xBC60"""

    _fields_ = [
        ("unknown_ints", c_uint32 * 16),  # +0x0
        # total 0x40 bytes
    ]


assert_struct_size(UnknownIntsAt_0xBC60, 0x40)


class UnknownShortsAt_0xBCB0(MarshalStructure):
    """Starts at offset 0xBCB0"""

    _fields_ = [
        ("unknown_shorts", c_uint16 * 12),  # +0x0
        ("padding", c_uint32),  # +0x18
        # total 0x1C bytes
    ]


assert_struct_size(UnknownShortsAt_0xBCB0, 0x1C)


class UnknownIntsAt_0xBCCC(MarshalStructure):
    """Starts at offset 0xBCCC"""

    _fields_ = [
        ("unknown_ints", c_uint32 * 10),  # +0x0
        # total 0x28 bytes
    ]


assert_struct_size(UnknownIntsAt_0xBCCC, 0x28)


class DLCRedeemedStateStruct(MarshalStructure):
    """Starts at offset 0xBD40"""

    _fields_ = [
        ("state_bytes", c_uint32 * 100),  # +0x0
        # total 0x288 bytes
    ]


GRACES_F_DLC_REDEEMED_STATUS_OFFSET = 0xBD40
assert_struct_size(DLCRedeemedStateStruct, 0x190)


class UnknownIntsAt_0xC1F0(MarshalStructure):
    """Starts at offset 0xC1F0"""

    _fields_ = [
        ("unknown_ints", c_uint32 * 65),  # +0x0
        # total 0x104 bytes
    ]


assert_struct_size(UnknownIntsAt_0xC1F0, 0x104)


class UnknownFloatsAt_0xC438(MarshalStructure):
    """Starts at offset 0xC438"""

    _fields_ = [
        ("unknown_float", c_float * 4),  # +0x0
        # total 0x10 bytes
    ]


assert_struct_size(UnknownFloatsAt_0xC438, 0x10)


class SideQuestData(MarshalStructure):
    """Starts at offset 0xC460"""

    _fields_ = [
        ("side_quest_ints", c_uint32 * 8),  # +0x0
        # total 0x20 bytes
    ]


assert_struct_size(SideQuestData, 0x20)


class UnknownBitmapAt0xC4D4(MarshalStructure):
    """Starts at offset 0xC4D4"""

    _fields_ = [
        ("unknown_bitmaps", c_uint32 * 3),  # +0x0
        # total 0xC bytes
    ]


assert_struct_size(UnknownBitmapAt0xC4D4, 0xC)


class UnknownIntAt_0xC5E4(MarshalStructure):
    """Starts at offset 0xC5E4"""

    _fields_ = [
        ("unknown_int", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(UnknownIntAt_0xC5E4, 0x4)


class UnknownIntAt_0xC5EC(MarshalStructure):
    """Starts at offset 0xC5EC"""

    _fields_ = [
        ("unknown_int", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(UnknownIntAt_0xC5EC, 0x4)


class UnknownIntAt_0x10500(MarshalStructure):
    """Starts at offset 0x10500"""

    _fields_ = [
        ("unknown_int", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(UnknownIntAt_0x10500, 0x4)


class UnknownIntAt_0x1057C(MarshalStructure):
    """Starts at offset 0x1057C"""

    _fields_ = [
        ("unknown_int", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(UnknownIntAt_0x1057C, 0x4)


class UnknownFloatAt_0x105C4(MarshalStructure):
    """Starts at offset 0x105C4"""

    _fields_ = [
        ("unknown_float", c_float),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(UnknownFloatAt_0x105C4, 0x4)


class UnknownIntAt_0x1062C(MarshalStructure):
    """Starts at offset 0x1062C"""

    _fields_ = [
        ("unknown_int", c_uint32),  # +0x0
        # total 0x4 bytes
    ]


assert_struct_size(UnknownIntAt_0x1062C, 0x4)


class TalesOfGracesFSaveStruct(FillEndianSwapStructure):  # type: ignore[metaclass]
    """
    Structure providing a mapping for the entire Tales of Graces f TOGBIN.app
    raw save file
    """

    _size_ = GRACES_F_RAW_SAVE_SIZE
    _offset_fields_ = [
        OffsetField(0x4, ("player_location_offset", PlayerLocationOffsetStruct)),
        OffsetField(0x30, ("game_data", GameDataStruct)),
        OffsetField(0x64, ("character_data_array", CharacterDataStructArray)),
        OffsetField(0x76D4, ("gald_data", GaldDataStruct)),
        OffsetField(0x76D8, ("playtime_data", PlaytimeDataStruct)),
        OffsetField(0x76DC, ("shard_data_array", ShardDataArray)),
        OffsetField(0x7A04, ("weapon_data_array", WeaponDataArray)),
        OffsetField(0x8E88, ("armor_data_array", ArmorDataArray)),
        OffsetField(0x9FE4, ("gem_data_array", GemDataArray)),
        OffsetField(0xA634, ("item_data_array", AllItemsAmountArray)),
        OffsetField(0xAABC, ("collection_book_data", CollectorStateDataStruct)),
        OffsetField(0xABB8, ("stamps_received", StampsReceivedStruct)),
        OffsetField(0xABBC, ("new_item_array", NewItemArray)),
        OffsetField(0xABF8, ("eleth_data", ElethDataStruct)),
        OffsetField(0xAC1C, ("eleth_mixer_data", ElethMixerDataStruct)),
        OffsetField(0xAC20, ("encounters", EncounterDataStruct)),
        OffsetField(0xAC24, ("other_game_data_ints", OtherGameData)),
        OffsetField(0xAC40, ("max_hit_count", MaxHitCountStruct)),
        OffsetField(0xAC44, ("grade_shop_data", GradeShopDataStruct)),
        OffsetField(0xAC4C, ("shop_data?", ShopUnknownStructArrayAt_0xAC4C)),
        OffsetField(0xAE7C, ("unknown_shorts_at_0xAE7C", UnknownShortsAt_0xAE7C)),
        OffsetField(0xAF1C, ("discoveries_bitmap", DiscoveriesBitfieldDataStruct)),
        OffsetField(0xAF2C, ("unknown_bitmap_at_0xAF2C", UnknownBitfieldAt_0xAF2C)),
        OffsetField(0xAF4C, ("unknown_bitmap_at_0xAF4C", UnknownBitfieldAt_0xAF4C)),
        OffsetField(0xAF54, ("enemy_data", EnemyDataArray)),
        OffsetField(0xB0D8, ("unknown_shorts_at_0xB0D8", UnknownShortsAt_0xB0D8)),
        OffsetField(0xB3D8, ("unknown_shorts_at_0xB3D8", MoreUnknownShortsAt_0xB3D8)),
        OffsetField(0xB8B0, ("grade_bonus_data", GradeBonusDataStruct)),
        OffsetField(0xB8D0, ("unknown_struct_at_0xB8D0", UnknownStructArrayAt_0xB8D0)),
        OffsetField(0xB994, ("unknown_record_data", RecordDataUnknownStruct)),
        OffsetField(0xB9B0, ("record_data", RecordDataStruct)),
        OffsetField(0xBB70, ("unknown_struct_at_0xBB70", BattlePlaytimeGameDataStructAt_0xBB70)),
        OffsetField(0xBBB0, ("unknown_int_at_0xBBB0", UnknownIntAt_0xBBB0)),
        OffsetField(0xBBBC, ("unknown_struct_at_0xBBBC", UnknownStructAt_0xBBBC)),
        OffsetField(0xBC1C, ("unknown_ints_at_0xBC1C", UnknownIntsAt_0xBC1C)),
        OffsetField(0xBC60, ("unknown_ints_at_0xBC60", UnknownIntsAt_0xBC60)),
        OffsetField(0xBCB0, ("unknown_shorts_at_0xBCB0", UnknownShortsAt_0xBCB0)),
        OffsetField(0xBCCC, ("unknown_ints_at_0xBCCC", UnknownIntsAt_0xBCCC)),
        OffsetField(GRACES_F_DLC_REDEEMED_STATUS_OFFSET, ("dlc_redeemed_state", DLCRedeemedStateStruct)),
        OffsetField(0xC1F0, ("unknown_ints_at_0xC1F0", UnknownIntsAt_0xC1F0)),
        OffsetField(0xC438, ("unknown_floats_at_0xC438", UnknownFloatsAt_0xC438)),
        OffsetField(0xC460, ("side_quest_data", SideQuestData)),
        OffsetField(0xC4D4, ("unknown_inverted_bitmap_at_0xC4D4", UnknownBitmapAt0xC4D4)),
        OffsetField(0xC5E4, ("unknown_int_at_0xC5E4", UnknownIntAt_0xC5E4)),
        OffsetField(0xC5EC, ("unknown_int_at_0xC5EC", UnknownIntAt_0xC5EC)),
        OffsetField(0x10500, ("unknown_int_at_0x10500", UnknownIntAt_0x10500)),
        OffsetField(0x1057C, ("unknown_int_at_0x1057C", UnknownIntAt_0x1057C)),
        OffsetField(0x105C4, ("unknown_float_at_0x105C4", UnknownFloatAt_0x105C4)),
        OffsetField(0x1062C, ("unknown_int_at_0x1062C", UnknownIntAt_0x1062C)),
    ]


assert_struct_size(TalesOfGracesFSaveStruct, GRACES_F_RAW_SAVE_SIZE)
