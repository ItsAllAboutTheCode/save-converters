# The Legend of Heroes - Trails into Reverie Save Converter
Save Converter for The Legend of Heroes - Trails into Reverie.  
Supports PS4, PS5, PC.  

The PS4 and PS5 saves are the same format and decompressed size

## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py trails-into-reverie --help
```

Alternatively the script of `trails_into_reverie_save_converter.py` can be run directly
```bash
python ./save_convert/trails_of/reverie/trails_into_reverie_save_converter.py  --help
```

If using the executable version the command to run the tool is:
* Linux/Mac
```bash
./save_converter trails-into-reverie
```
* Windows
```powershell
.\save_converter.exe trails-into-reverie
```

### Example
#### Convert PS4/PS5 -> PC Trails into Reverie Save
```bash
python save_converter.py trails-into-reverie --convert-format=ps4-to-pc -i <path-to-ps4-save> -o <path-to-store-pc-save>
```
```bash
python save_converter.py trails-into-reverie --convert-format=ps5-to-pc -i <path-to-ps5-save> -o <path-to-store-pc-save>
```

#### Reverse Conversion
The reverse conversion from PC -> PS4 is supported.  
```bash
python save_converter.py trails-into-reverie --convert-format=pc-to-ps4 -i <path-to-pc-save> -o <path-to-store-ps4-save>
```
```bash
python save_converter.py trails-into-reverie --convert-format=pc-to-ps4 -i <path-to-pc-save> -o <path-to-store-ps5-save>
```

#### Decompress Input File Only
The input file can be decompressed without conversion to different format.  
Supported compression types are: `Falcom Type1` and `Zstandard` (ZSTD)
```bash
python save_converter.py trails-into-reverie --decompress-only -i <path-to-compressed-save> -o <path-to-decompressed-save>
```

## Credits
AdmiralCurtiss [SenPatcher](https://github.com/AdmiralCurtiss/SenPatcher) repo - For the Type 1 Decompression algorithm
