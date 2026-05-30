# Tales of Xilia Remastered Save Decrypter/Encrypter
Save Decrypter/Encrypter for Tales of Xillia Remastered   
It supports decryption/encryption of saves between for PC, PS4, PS5, Nintendo Switch, Xbox One, Xbox Series S|X saves.  

# Features

## Save Decryption
Decrypts a Tales of Xillia Remastered save to a JSON file.  

## Save Encryption
Encrypt a JSON to a Tales of Xillia Remastered save.


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

#### Encrypt PC Save
```bash
python save_converter.py tales-of-xillia encrypt-save --save-format=pc -i <path-to-decrypted-pc-save> -o <path-to-store-encrypted-pc-save>
```

#### Decrypt Bundle.data
```bash
python save_converter.py tales-of-xillia decrypt-save --save-format=pc -i <path-to-encrypted-Bundle.data> -o <path-to-store-decrypted-Bundle.data>
```

#### Encrypt Remastered PC SaveList
```bash
python save_converter.py tales-of-xillia encrypt-save --save-format=pc -i <path-to-decrypted-Bundle.data> -o <path-to-store-encrypted-Bundle.data>
```


## Credits

Nenkai  - for his implementation of a Save Encrypter/Decrypter in C#: https://github.com/Nenkai/ToXRSaveCryptor
