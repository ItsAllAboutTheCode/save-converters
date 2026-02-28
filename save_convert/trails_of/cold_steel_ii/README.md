# The Legend of Heroes - Trails of Cold Steel II Save Converter
Save Converter for The Legend of Heroes - Trails of Cold Steel II.  
Supports PS4, PC.  

## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py trails-of-cold-steel-ii --help
```

### Example
#### Convert PS4 -> PC Trails of Cold Steel II Save
```bash
python save_converter.py trails-of-cold-steel-ii --convert-format=ps4-to-pc -i <path-to-ps4-save> -o <path-to-store-pc-save>
```

#### Reverse Conversion
The reverse conversion from PC -> PS4 is experimental and untested, however it is performed by reversing the PS4 -> PC patch table
```bash
python save_converter.py trails-of-cold-steel-ii --convert-format=pc-to-ps4 -i <path-to-pc-save> -o <path-to-store-ps4-save>
```

## Credits
AdmiralCurtiss [SenPatcher](https://github.com/AdmiralCurtiss/SenPatcher) repo - For the Type 1 Decompression algorithm
