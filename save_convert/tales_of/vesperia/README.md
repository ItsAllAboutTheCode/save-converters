# Tales of Vesperia Save Converter
Save Converter for Tales of Vesperia.  
Supports PS3, PC.  

## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py tales-of-vesperia --help
```

### Example
#### Convert PS3 -> PC Vesperia Save
```bash
python save_converter.py tales-of-vesperia --convert-format=ps3-to-pc -i <path-to-ps3-save> -o <path-to-store-pc-save>
```

####  Convert PC -> PS3 Vesperia Save
```bash
python save_converter.py tales-of-vesperia --convert-format=pc-to-ps3 -i <path-to-pc-save> -o <path-to-store-ps3-save>
```

---
### Note
The save file header has been modified in minimal fashion as to make a round trip conversion PS3 <-> PC possible when the `--no-patch-dlc-item-checks` option is used.  
Therefore the saves in the load menu will look awkward, however the saves should load correctly and once resaved the header will be fixed for the appropriate platform.

The [](./cheat_tables) folder also contains a cheat table for patching the DLC item checks when loading a Vesperia save as well.  
This can be used in conjunction with the `--no-patch-dlc-item-checks` to allow a converted PS3 -> PC save that is round trip-able to be loaded on PC if it contains DLC.

## Credits
AdmiralCurtiss [HyoutaTools](https://github.com/AdmiralCurtiss/HyoutaTools) repo - Used to learn about the save format as well as to get a list of Title IDs
