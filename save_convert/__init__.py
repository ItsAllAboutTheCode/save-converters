# Map of game name to save  converter modules
from typing import NamedTuple, TypeAlias


class ModuleInfo(NamedTuple):
    # Path to the module containing converter functionality
    module: str
    # List of aliases for the module subparser
    aliases: list[str] = []


ConverterModules: TypeAlias = dict[str, ModuleInfo]
converter_modules: ConverterModules = {
    "tales-of-arise": ModuleInfo("save_convert.tales_of.arise.tales_of_arise_save_converter", ["arise"]),
    "tales-of-vesperia": ModuleInfo("save_convert.tales_of.vesperia.tales_of_vesperia_save_converter", ["vesperia"]),
    "trails-of-cold-steel-i": ModuleInfo(
        "save_convert.trails_of.cold_steel_i.trails_of_cold_steel_i_save_converter",
        aliases=["cold-steel", "cold-steel-i"],
    ),
    "trails-of-cold-steel-ii": ModuleInfo(
        "save_convert.trails_of.cold_steel_ii.trails_of_cold_steel_ii_save_converter", aliases=["cold-steel-ii"]
    ),
    "trails-of-cold-steel-iii": ModuleInfo(
        "save_convert.trails_of.cold_steel_iii.trails_of_cold_steel_iii_save_converter", aliases=["cold-steel-iii"]
    ),
    "trails-of-cold-steel-iv": ModuleInfo(
        "save_convert.trails_of.cold_steel_iv.trails_of_cold_steel_iv_save_converter", aliases=["cold-steel-iv"]
    ),
    "trails-into-reverie": ModuleInfo(
        "save_convert.trails_of.reverie.trails_into_reverie_save_converter", aliases=["reverie"]
    ),
}
