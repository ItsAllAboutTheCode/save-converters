# Tales of Xilia Remastered Save Decrypter/Encrypter
Save Converter/Decrypter/Encrypter for Tales of Xillia Remastered   
It supports decryption/encryption of saves between for PC, PS4, PS5, Nintendo Switch, Xbox One, Xbox Series S|X saves.  

It also supports converting the PS3 Save <-> Remastered Platform Save

# Features

## Save Decryption
Decrypts a Tales of Xillia Remastered save to a JSON file.  

## Save Encryption
Encrypt a JSON to a Tales of Xillia Remastered save.

## Save Conversion
Convert a Save from either PS3 -> a Remastered game platform or vice versa

Notes about the research of the conversion algorithm can be found in the [save_NOTES](./save_NOTES.md) document.  


## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py tales-of-xillia --help
```

Alternatively the script of `tales_of_xillia_save_converter.py` can be run directly
```bash
python ./save_convert/tales_of/xillia/tales_of_xillia_save_converter.py  --help
```

#### Decrypt PC Save
```bash
python save_converter.py tales-of-xillia decrypt-save --save-format=pc -i <path-to-encrypted-pc-save> -o <path-to-store-decrypted-pc-save>
```

The actual raw Save Block Data is stringified JSON inside of the `mSaveBlockData` key.  

The stringified JSON can be dumped as separate JSON files using the `-d/--dump-save-block-data` option.  
```bash
python save_converter.py tales-of-xillia decrypt-save -s pc -i <path-to-encrypted-pc-save> -o <path-to-store-decrypted-pc-save> -d
```

The Save Block JSON files will be placed in a folder with the name of `path-to-store-decrypted-pc-save>.save-block-data`.  

#### Encrypt PC Save
```bash
python save_converter.py tales-of-xillia encrypt-save --save-format=pc -i <path-to-decrypted-pc-save> -o <path-to-store-encrypted-pc-save>
```

#### Decrypt Bundle.data

The decrypting the Bundle data is useful when needing to add a new save to load to game instead of overriding an existing save.  
Steps for how to add a new save is detailed in the Save Notes [PC-Only: Remastered Platform Bundle Data](./save_NOTES.md#pc-only-remastered-platform-bundle-data) section
```bash
python save_converter.py tales-of-xillia decrypt-save --save-format=pc -i <path-to-encrypted-Bundle.data> -o <path-to-store-decrypted-Bundle.data>
```

#### Encrypt Remastered Bundle.data
```bash
python save_converter.py tales-of-xillia encrypt-save --save-format=pc -i <path-to-decrypted-Bundle.data> -o <path-to-store-encrypted-Bundle.data>
```

#### Convert PS3 Save -> PC Save
Prereq: The PS3 save has been decrypted with Apollo or some other tool.  
```bash
python save_converter.py tales-of-xillia convert-save --convert-format=ps3-to-pc -i <path-to-ps3-save> -o <path-to-store-encrypted-pc-save>
```

The conversion can also dump the decrypted SaveData JSON as well as decrypted JSON files for each save block.  
The `-d/--debug` option can be provided to trigger this behavior.  
```bash
python save_converter.py tales-of-xillia convert-save -f ps3-to-pc -i <path-to-ps3-save> -o <path-to-store-encrypted-pc-save> -d
```

The SaveData JSON file will be placed at `<path-to-store-encrypted-pc-save>.debug`.  
The Save Block JSON files will be placed in a folder with the name of `<path-to-store-encrypted-pc-save>.debug.save-block-data`.  

#### Convert PC Save -> PS3 Save
A encrypted or decrypted PC save can be converted to a PS3 save via the convert-save action as well.  
```bash
python save_converter.py tales-of-xillia convert-save --convert-format=pc-to-ps3 -i <path-to-pc-save> -o <path-to-store-ps3-save>
```


## Credits

Nenkai - For his implementation of a Save Encrypter/Decrypter in C#: https://github.com/Nenkai/ToXRSaveCryptor
