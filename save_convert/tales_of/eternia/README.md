# Tales of Eternia Remastered Save Decrypter/Encrypter
Save Decrypter/Encrypter for Tales of Eternia Remastered   
It supports decryption/encryption of saves between for PC, PS4, PS5, Nintendo Switch (2), Xbox Series S|X saves.  

# Features

## Save Decryption
Decrypts a Tales of Eternia Remastered save to a raw binary file.  

## Save Encryption
Encrypt a raw binary file to a Tales of Eternia Remastered save.


Notes about the research of the conversion algorithm can be found in the [save_NOTES](./save_NOTES.md) document.  


## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py tales-of-eternia --help
```

Alternatively the script of `tales_of_eternia_save_converter.py` can be run directly
```bash
python ./save_convert/tales_of/eternia/tales_of_eternia_save_converter.py --help
```

If using the executable version the command to run the tool is:
* Linux/Mac
```bash
./save_converter tales-of-eternia
```
* Windows
```powershell
.\save_converter.exe tales-of-eternia
```

#### Decrypt PC Save
```bash
python save_converter.py tales-of-eternia decrypt-save --save-format=pc -i <path-to-encrypted-pc-save> -o <path-to-store-decrypted-pc-save>
```


#### Encrypt PC Save
```bash
python save_converter.py tales-of-eternia encrypt-save --save-format=pc -i <path-to-decrypted-pc-save> -o <path-to-store-encrypted-pc-save>
```

#### Decrypt List Data

The list data contains the entry of saves available for load in the load menu.  
This is useful when needing to add a new save to load to game instead of overriding an existing save.  
```bash
python save_converter.py tales-of-eternia decrypt-save --save-format=pc -i <path-to-encrypted-ListData> -o <path-to-store-decrypted-ListData>
```

#### Encrypt List Data
```bash
python save_converter.py tales-of-eternia encrypt-save --save-format=pc -i <path-to-decrypted-ListData> -o <path-to-store-encrypted-ListData>
```

#### Decrypt System Save

The system save contains system specific settings, such as graphic resolution and input mappings.  
This save can also be decrypted using the same command as above.  
```bash
python save_converter.py tales-of-eternia decrypt-save --save-format=pc -i <path-to-encrypted-ListData> -o <path-to-store-decrypted-ListData>
```

#### Encrypt System Save
```bash
python save_converter.py tales-of-eternia encrypt-save --save-format=pc -i <path-to-decrypted-ListData> -o <path-to-store-encrypted-ListData>
```


## Credits

NeXoGone - For decompiling the save routine and generated a save decryptor/encryptor for it
