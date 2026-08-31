# Console Save <-> PC Save Conversion scripts

The scripts in this repo are used for converting decrypted saves of console games (PS3, PS4, PS5) to their PC equivalents.  
The list of games of supported games are enumerated in the [How to use](#how-to-use) section below.  


## How to use

There are various tools that can be used to get decrypted console savedata content.

### Decryption Tools

| Console | Decryption Tool |
| :--- | :--- |
| PS3 | [Apollo Save Tool (PS3)](https://github.com/bucanero/apollo-ps3) |
| PS4 | [Apollo Save Tool (PS4)](https://github.com/bucanero/apollo-ps4) |
| PS5 | [Garlic SaveMgr for PS5](https://git.earthonion.com/earthonion/garlic-savemgr) |



## Getting Started

### Installing required python dependencies (non-PyInstaller executable version ONLY)

NOTE:  
Only required when running python scripts directly.  
Not needed when running the executable from the Releases page. 


The save converter dependencies on other python packages that can be installed using a python package manager such as `pip` or `uv`.  
```bash
uv sync
```
or
```bash
pip install -e .
```
## Usage

Available converters can found by running the command (Only for Python scripts)  
```bash
python save_converter.py --help
```

### IMPORTANT: Windows users read this
Or if using the executable version of the save converter script  
```
save_converter --help
```

### Save Converters/Decrypters

Save converters or decrypters are supported for the following games:

| Game | Script | Cheat Tables |
| :--- | :--- | :-- |
| Tales of Arise | [tales-of-arise-converter-decrypter](./save_convert/tales_of/arise/README.md) | None |
| Tales of Berseria | [tales-of-beseria-remastered-convert-notes](./save_convert/tales_of/berseria/README.md) | None |
| Tales of Graces f | [tales-of-graces-f-converter-decrypter](./save_convert/tales_of/graces/README.md) | None |
| Tales of Vesperia | [tales-of-vesperia-converter](./save_convert/tales_of/vesperia/README.md) | [tales-of-vesperia-cheat-tables](./save_convert/tales_of/vesperia/cheat_tables) |
| Tales of Xillia | [tales-of-xillia-converter-decrypter](./save_convert/tales_of/xillia/README.md) | None |
| The Legend of Heroes - Trails of Cold Steel I | [trails-of-cold-steel-i-converter](./save_convert/trails_of/cold_steel_i/README.md) | [trails-of-cold-steel-i-cheat-tables](./save_convert/trails_of/cold_steel_i/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel II | [trails-of-cold-steel-ii-converter](./save_convert/trails_of/cold_steel_ii/README.md) | [trails-of-cold-steel-ii-cheat-tables](./save_convert/trails_of/cold_steel_ii/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel III | [trails-of-cold-steel-iii-converter](./save_convert/trails_of/cold_steel_iii/README.md) | [trails-of-cold-steel-iii-cheat-tables](./save_convert/trails_of/cold_steel_iii/cheat_tables) |
| The Legend of Heroes - Trails of Cold Steel IV | [trails-of-cold-steel-iv-converter](./save_convert/trails_of/cold_steel_iv/README.md) | [trails-of-cold-steel-iv-cheat-tables](./save_convert/trails_of/cold_steel_iv/cheat_tables) |
| The Legend of Heroes - Trails into Reverie | [trails-into-reverie-converter](./save_convert/trails_of/reverie/README.md) | [trails-into-reverie-cheat-tables](./save_convert/trails_of/reverie/cheat_tables) |
| The Legend of Heroes - Trails through Daybreak | No-Conversion Needed | [trails-through-daybreak-i-cheat-tables](./save_convert/trails_of/daybreak_i/cheat_tables) |
| The Legend of Heroes - Trails through Daybreak II | No-Conversion Needed | [trails-through-daybreak-ii-cheat-tables](./save_convert/trails_of/daybreak_ii/cheat_tables) |
| The Legend of Heroes - Trails beyond the Horizon | No-Conversion Needed | [trails-beyond-the-horizon-cheat-tables](./save_convert/trails_of/horizon/cheat_tables) |


## Contributors Notes

See [CONTRIBUTING.md](./CONTRIBUTING.md)

### Running static analysis
Static analysis can be run locally using the `hatch` build tool
#### Check static analysis
```bash
hatch env run -e lint lint
```
#### Fix lint issues
```bash
hatch env run -e lint lint-action
```


## Requirements
### Running PyInstaller executable
If running the executable generated from using `PyInstaller` tool, then a specific version of Python is not required.  
All executables on the [Releases](https://github.com/ItsAllAboutTheCode/save-converters/releases) page are built using `PyInstaller`.  

* Steps to build a PyInstaller executable is listed in the [Building PyInstaller executable](./CONTRIBUTING.md#building-pyinstaller-executable) section of the `CONTRIBUTING.md` file.  

### Running Python script directly
`Trails` save converter requirements: Python 3.14\+
* This is needed for access to the [Zstandard](https://docs.python.org/3/whatsnew/3.14.html#pep-784-zstandard-support-in-the-standard-library) module.  

`Tales of` save converters requirements: Python 3.12\+


## Tutorial - How to use save converter via CLI

https://github.com/user-attachments/assets/ef165a15-1f5a-46fa-9d33-c8e3a3ac6428
