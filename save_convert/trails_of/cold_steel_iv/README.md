# The Legend of Heroes - Trails of Cold Steel IV Save Converter
Save Converter for The Legend of Heroes - Trails of Cold Steel IV.  
Supports PS4, PC.  

## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py trails-of-cold-steel-iv --help
```

### Example
#### Convert PS4 -> PC Trails of Cold Steel IV Save
```bash
python save_converter.py trails-of-cold-steel-iv --convert-format=ps4-to-pc -i <path-to-ps4-save> -o <path-to-store-pc-save>
```

#### Reverse Conversion
The reverse conversion from PC -> PS4 is supported.  
```bash
python save_converter.py trails-of-cold-steel-iv --convert-format=pc-to-ps4 -i <path-to-pc-save> -o <path-to-store-ps4-save>
```

#### Decompress Input File Only
The input file can be decompressed without conversion to different format.  
Supported compression types are: `Falcom Type1` and `Zstandard` (ZSTD)
```bash
python save_converter.py trails-of-cold-steel-iv --decompress-only -i <path-to-compressed-save> -o <path-to-decompressed-save>
```

## Credits
AdmiralCurtiss [SenPatcher](https://github.com/AdmiralCurtiss/SenPatcher) repo - For the Type 1 Decompression algorithm
