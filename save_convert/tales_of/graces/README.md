# Tales of Graces f Remastered Save Converter, Decrypter/Encrypter and YAML converter
Save Converter for Tales of Graces f Remastered that can decrypt/encrypt saves as well.  
It supports conversion of saves between PS3 <-> PC, PS4, PS5, Nintendo Switch, Xbox One, Xbox Series S|X saves.  
The tool also converting raw save files to YAML for save editing.  

# Features

## Save Conversion
Converts a save between two platforms from one format to another.  
In actuality the only platforms that differ in save format are non-PS3 platforms vs PS3 platforms.  
So this feature is only used to convert saves `PS3 <-> non-PS3(PC/PS5/NSW/etc...)` platforms.  
Supports all platforms.  

## Save Decryption
Decrypts a Tales of Graces f Remastered save to a folder containing a ICON0.png, TOGAPP.bin and TOGNOBLE.bin containg the raw save data.  
The TOGAPP.bin data is in little endian byteorder.  
Supports only Tales of Graces f Remastered platforms (PS3 not supported).

## Save Encryption
Encrypt a folder containg a TOGBIN.app file to a Tales of Graces f Remastered save.
Supports encrypting a raw PS3 save file as well.  
Supports only Tales of Graces f Remastered platforms (PS3 not supported).  

## Savelist Decryption
Decrypts a Tales of Graces f Remastered SaveDataList.sav file to a JSON file for editing.  
The SaveDataList.save is used to list the available saves on the save load menu.  
Supports only Tales of Graces f Remastered platforms (PS3 not supported).  

## Savelist Encryption
Encrypts a JSON file to a Tales of Graces f Remastered SaveDataList.sav file.  
Supports only Tales of Graces f Remastered platforms (PS3 not supported).  

## PNG to SaveData.json Conversion
Converts a PNG file to Tales of Graces F Remastered JSON template file.  
The Metadata JSON file can then be encrypted along the raw save file (TOGAPP.bin) to create a Tales of Graces f Remastered save with a custom thumbnail.  

## PNG Extraction from SaveData.json
Extracts the ICON0 PNG file from a decrypted Tales of Graces f Remastered save JSON file.  
The result is the thumbnail file shown during loading of a save.  

## Convert a Binary Save file to YAML file
Convert a raw native binary `Tales of Graces f` / `Tales of Graces f Remastered`" save to YAML for editing.  
The YAML file can be dumped with comments detailing the offsets from the binary save file.  
The Save Format for binary file must be specified to correct convert to YAML.  
Supports all platforms including PS3.

## Convert a YAML file to Binary Save file
Convert a YAML file containing save data for `Tales of Graces f` back into a raw native binary file.  
The Save Format for binary must be specified to allow converting to correct format for the output platform.  
Specifying a save format of `PS3` allows the Binary Save file to be directly loaded on PS3 system.  
Specifying a save format for any Remastered platform(PC, PS5, NSW, etc...) creates the Binary Save file, which would then need to use the Save Encryption format to create a loadable save.  
Supports all platforms including PS3.

## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py tales-of-graces-f --help
```

Alternatively the script of `tales_of_graces_f_save_converter.py` can be run directly
```bash
python ./save_convert/tales_of/graces/tales_of_graces_f_save_converter.py --help
```

If using the executable version the command to run the tool is:
* Linux/Mac
```bash
./save_converter tales-of-graces-f
```
* Windows
```powershell
.\save_converter.exe tales-of-graces-f
```

### Example
#### Convert PS3 Save -> PC Graces f Remastered Save
```bash
python save_converter.py tales-of-graces-f convert-save --convert-format=ps3-to-pc -i <path-to-ps3-save> -o <path-to-store-encrypted-pc-save>
```


#### Convert Encrypted PC -> PS3 Graces f Remastered Save
```bash
python save_converter.py tales-of-graces-f convert-save --convert-format=pc-to-ps3 -i <path-to-pc-encrypted-save> -o <path-to-store-ps3-save>
```

#### Decrypt PC Save
```bash
python save_converter.py tales-of-graces-f decrypt-save --save-format=pc -i <path-to-encrypted-pc-save> -o <path-to-store-decrypted-pc-save>
```

#### Encrypt PC Save
```bash
python save_converter.py tales-of-graces-f encrypt-save --save-format=pc -i <path-to-decrypted-pc-save> -o <path-to-store-encrypted-pc-save>
```

#### Decrypt Remastered PC SaveList
```bash
python save_converter.py tales-of-graces-f decrypt-savelist --save-format=pc -i <path-to-encrypted-savelist> -o <path-to-store-decrypted-savelist>
```

#### Encrypt Remastered PC SaveList
```bash
python save_converter.py tales-of-graces-f encrypt-savelist --save-format=pc -i <path-to-decrypted-savelist> -o <path-to-store-encrypted-savelist>
```

#### Decrypt Remastered PC System Save
```bash
python save_converter.py tales-of-graces-f decrypt-system-save --save-format=pc -i <path-to-encrypted-system-save> -o <path-to-store-decrypted-system-save-folder>
```

#### Encrypt Remastered PC System Save
```bash
python save_converter.py tales-of-graces-f encrypt-system-save --save-format=pc -i <path-to-decrypted-system-save-folder> -o <path-to-store-encrypted-system-save>
```

#### Convert PNG to Remastered Save JSON template
```bash
python save_converter.py tales-of-graces-f convert-png-to-json --save-format=pc -i <path-to-decrypted-SaveData.json> -o <path-to-store-PNG>
```

#### Extract PNG from Remastered PC Save
```bash
python save_converter.py tales-of-graces-f convert-json-to-png --save-format=pc -i <path-to-PNG> -o <path-to-store-decrypted-SaveData.json>
```

#### Convert PS3 Save to YAML (With comments in YAML)
```bash
python save_converter.py tales-of-graces-f convert-save-to-yaml --save-format=ps3 -i <path-to-ps3-save> -o <path-to-store-yaml> --with-comments
```

#### Convert YAML data to back to PS3 Save
```bash
python save_converter.py tales-of-graces-f convert-yaml-to-save --save-format=ps3 -i <path-to-yaml> -o <path-to-store-ps3-save> 
```

#### Convert other platforms (PC/PS4/PS5/NSW, etc...) encrypted saves Save to YAML (With comments in YAML)
```bash
# Decrypt save
python save_converter.py tales-of-graces-f decrypt-save --save-format=pc -i <path-to-encrypted-pc-save> -o <path-to-decrypted-pc-save>
# Convert to yaml (with annotations of dumped offsets)
python save_converter.py tales-of-graces-f convert-save-to-yaml --save-format=pc -i <path-to-decrypted-pc-save>/TOGAPP.bin -o <path-to-store-yaml> --with-comments
```

#### Convert YAML data to other platforms (PC/PS4/PS5/NSW, etc...) as an encrypted save
```bash
# Convert yaml back to raw save binary
python save_converter.py tales-of-graces-f convert-yaml-to-save --save-format=pc -i <path-to-store-yaml> -o <path-to-decrypted-pc-save>/TOGAPP.bin
# Encrypt save
python save_converter.py tales-of-graces-f encrypt-save --save-format=pc -i <path-to-decrypted-pc-save> -o <path-to-store-encrypted-pc-save>
```


## Credits

Sora3100 - For the CheatTables containing offsets of game data structures at [Graces_F_PC.CT](https://github.com/Sora3100/Tales_of_Cheat_Tables/blob/master/Graces_F_PC.CT).  
The layout of the in-memory game structure matches the save structure.  
