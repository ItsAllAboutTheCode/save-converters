# Console Save <-> PC Save Conversion scripts

The scripts in this repo are used for converting decrypted saves of console games to their PC equivalents.  
The list of games of supported games are enumarated in the [How to use](#how-to-use) section below.

## How to use

Scripts converters are supported for the following games:

| Game | Script | Cheat Tables |
| :--- | :--- | :-- |
| Tales of Vesperia | [tales-of-vesperia-converter](./save_convert/tales_of/vesperia/README.md) | [tales-of-vesperia-cheat-tables](./save_convert/tales_of/vesperia/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel I | [trails-of-cold-steel-i-converter](./save_convert/trails_of/cold_steel_i/README.md) | [trails-of-cold-steel-i-cheat-tables](./save_convert/trails_of/cold_steel_i/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel II | [trails-of-cold-steel-ii-converter](./save_convert/trails_of/cold_steel_ii/README.md) | [trails-of-cold-steel-ii-cheat-tables](./save_convert/trails_of/cold_steel_ii/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel III | [trails-of-cold-steel-iii-converter](./save_convert/trails_of/cold_steel_iii/README.md) | [trails-of-cold-steel-iii-cheat-tables](./save_convert/trails_of/cold_steel_iii/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel IV | [trails-of-cold-steel-iv-converter](./save_convert/trails_of/cold_steel_iv/README.md) | [trails-of-cold-steel-iv-cheat-tables](./save_convert/trails_of/cold_steel_iv/cheat_tables) |
| The Legend of Heroes - Trails into Reverie | [trails-into-reverie-converter](./save_convert/trails_of/reverie/README.md) | [trails-into-reverie-cheat-tables](./save_convert/trails_of/cold_steel_iv/cheat_tables) |


## Contributors Notes

See [CONTRIBUTING.md](./CONTRIBUTING.md)

### Running static analysis
Static analysis can be run locally using the `hatch` build tool
#### Check static analysis
```bash
hatch env run -e lint lint-action
```
#### Fix lint issues
```bash
hatch env run -e lint lint
```


## Requirements
### Running PyInstaller executable
If running the executable generated from using `PyInstaller` tool, then a specific version of Python is not required.  
All executables on the [Releases](https://github.com/ItsAllAboutTheCode/save-converters/releases) page are built using `PyInstaller`.  

* Steps to build a PyInstaller executable is listed in the [Building PyInstaller executable](./CONTRIBUTING.md#building-pyinstaller-executable) section of the `CONTRIBUTING.md` file.  

### Running Python script directly
`Trails` save converter requirements: Python 3.14\+
* This is needed for access to the [Zstandard](https://docs.python.org/3/whatsnew/3.14.html#pep-784-zstandard-support-in-the-standard-library) module.  

`Tales of Vesperia` save converter requirements: Python 3.12\+

