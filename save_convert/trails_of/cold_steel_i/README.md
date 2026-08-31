# The Legend of Heroes - Trails of Cold Steel I Save Converter
Save Converter for The Legend of Heroes - Trails of Cold Steel I.  
Supports PS4, PC.  

## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py trails-of-cold-steel-i --help
```

Alternatively the script of `trails_of_cold_steel_i_save_converter.py` can be run directly
```bash
python ./save_convert/trails_of/cold_steel_i/trails_of_cold_steel_i_save_converter.py --help
```

If using the executable version the command to run the tool is:
* Linux/Mac
```bash
./save_converter trails-of-cold-steel-i
```
* Windows
```powershell
.\save_converter.exe trails-of-cold-steel-i
```

### Example
#### Convert PS4 -> PC Trails of Cold Steel IV Save
```bash
python save_converter.py trails-of-cold-steel-i --convert-format=ps4-to-pc -i <path-to-ps4-save> -o <path-to-store-pc-save>
```

#### Reverse Conversion
The reverse conversion from PC -> PS4 is supported.  
```bash
python save_converter.py trails-of-cold-steel-i --convert-format=pc-to-ps4 -i <path-to-pc-save> -o <path-to-store-ps4-save>
```

## Save Conversion Notes
Research notes for save conversion is detailed in the [save_NOTES.md](./save_NOTES.md)

## Credits
AdmiralCurtiss [SenPatcher](https://github.com/AdmiralCurtiss/SenPatcher) repo - For the Type 1 Decompression algorithm
