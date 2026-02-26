# Console Save <-> PC Save Conversion scripts

The scripts in this repo are used for converting decrypted saves of console games to their PC equivalents.  
The list of games of supported games are enumarated in the [How to use](#how-to-use) section below.

## How to use

Scripts converters are supported for the following games:

| Game | Script | Cheat Tables |
| :--- | :--- | :-- |
| Tales of Vesperia | [vesperia-converter](./save_convert/tales_of/vesperia/README.md) | [vesperia-cheat-tables](./save_convert/tales_of/vesperia/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel I | [trails-of-cold-steel-i-converter](./save_convert/trails_of/cold_steel_i/README.md) | [trails-of-cold-steel-iv-cheat-tables](./save_convert/trails_of/cold_steel_i/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel II | [trails-of-cold-steel-ii-converter](./save_convert/trails_of/cold_steel_ii/README.md) | [trails-of-cold-steel-iv-cheat-tables](./save_convert/trails_of/cold_steel_ii/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel III | [trails-of-cold-steel-iii-converter](./save_convert/trails_of/cold_steel_iii/README.md) | [trails-of-cold-steel-iv-cheat-tables](./save_convert/trails_of/cold_steel_iii/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel IV | [trails-of-cold-steel-iv-converter](./save_convert/trails_of/cold_steel_iv/README.md) | [trails-of-cold-steel-iv-cheat-tables](./save_convert/trails_of/cold_steel_iv/cheat_tables) |
| The Legend of Heroes - Trails into Reverie | [trails-into-reverie-converter](./save_convert/trails_of/reverie/README.md) | [trails-into-reverie-cheat-tables](./save_convert/trails_of/cold_steel_iv/cheat_tables) |


## Contributors Notes

To register a new converter the following steps can be performed:  

1. Create a new python module that implements the save conversion between formats
1. Add a `def add_commands(parser: argparse.ArgumentParser)` method within the converter to register a subparser to invoke the converter command
1. Inside the `add_commands` method use the `parser.set_defaults(func=<name-of-function-to-perform-conversion>)` to register a hook function that performs the save conversion
1. Add the absolute module path to the new python module in [](save_convert/__init__.py) to the `converter_modules` dictionary.  
   Ex. `converter_modules["game_name"]: "save_convert.path.to.module",`

### Running static analysis
Static analysis can be run locally using the `hatch` build tool
#### Check static analysis
```bash
hatch env run -e lint lint
```
#### Fix lint actions
```bash
hatch env run -e lint lint-action
```


## Requirements
[Python 3.14+](https://docs.python.org/3/whatsnew/3.14.html#pep-784-zstandard-support-in-the-standard-library) is needed for access to the Zstandard module.  
