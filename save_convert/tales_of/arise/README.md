# Tales of Arise Save Converter and Decrypter
Save Converter for Tales of Arise that can decrypt/encrypt saves as well.  
It supports PS4, PS5, PC saves with untested support for Xbox One and Xbox Series X/S saves.  
Furthermore the decrypted save item section blocks offsets can be dumped using this tool, which can be used for save editing.  

## Usage
Information on supported options can be found by running the following command from the root of the repo.
```bash
python save_converter.py tales-of-arise --help
```

Alternatively the script of `tales_of_arise_save_conveter.py` can be run directly
```bash
python ./save_convert/tales_of/arise/tales_of_arise_save_converter.py  --help
```

### Example
#### Convert Encrypted PS5 -> PC Arise Save
```bash
python save_converter.py tales-of-arise convert-save --convert-format=ps5-to-pc -i <path-to-encrypted-ps5-save> -o <path-to-store-encrypted-pc-save>
```

#### Convert Encrypted PS4 -> PC Arise Save
```bash
python save_converter.py tales-of-arise convert-save --convert-format=ps4-to-pc -i <path-to-encrypted-ps4-save> -o <path-to-store-encrypted-pc-save>
```

#### Convert Encrypted PC -> PS5 Arise Save
```bash
python save_converter.py tales-of-arise convert-save --convert-format=pc-to-ps5 -i <path-to-pc-encrypted-save> -o <path-to-store-encrypted-ps5-save>
```

#### Convert Decrypted PS5 -> PC Arise Save
```bash
python save_converter.py tales-of-arise convert-decrypted-save --convert-format=ps5-to-pc -i <path-to-ps5-decrypted-save> -o <path-to-store-decrypted-pc-save>
```

#### Convert Decrypted PC -> PS5 Arise Save
```bash
python save_converter.py tales-of-arise convert-decrypted-save --convert-format=pc-to-ps5 -i <path-to-decrypted-pc-save> -o <path-to-store-decrypted-ps5-save>
```

#### Decrypt PS5 Save
```bash
python save_converter.py tales-of-arise decrypt-save --save-format=ps5 -i <path-to-encrypted-ps5-save> -o <path-to-store-decrypted-ps5-save>
```

#### Decrypt PC Save
```bash
python save_converter.py tales-of-arise decrypt-save --save-format=pc -i <path-to-encrypted-pc-save> -o <path-to-store-decrypted-pc-save>
```

#### Encrypt PS5 Save
```bash
python save_converter.py tales-of-arise encrypt-save --save-format=ps5 -i <path-to-decrypted-ps5-save> -o <path-to-store-encrypted-ps5-save>
```

#### Encrypt PC Save
```bash
python save_converter.py tales-of-arise encrypt-save --save-format=pc -i <path-to-decrypted-pc-save> -o <path-to-store-encrypted-pc-save>
```

#### Dump PS5 Save Section Offsets
```bash
python save_converter.py tales-of-arise dump-save-offsets --save-format=pc -i <path-to-decrypted-ps5-save>
```

#### Dump PC Save Section Offsets
```bash
python save_converter.py tales-of-arise dump-save-offsets --save-format=pc -i <path-to-decrypted-pc-save>
```

---
### Save Notes
The save item sections in the save file are offsets based. Therefore the location of the save item sections aren't fixed.  
The decrypted dword at (PC offset=0x320A0, PS4/PS5 offset=0x32090) points to the save item header section, which points to first save item section block.  
Each save item block has contains an offset value at the block start address + 0xC that points to the next save item section.
The order of the blocks are as follows:
* Entitlement
* PartyOrder
* SaveData_GameConfig
* PartyProfile
* SaveData_ItemManager
* ArisePCStatus_000
* ArisePCStatus_001
* ArisePCStatus_002
* ArisePCStatus_003
* ArisePCStatus_004
* ArisePCStatus_005
* ArisePCStatus_006
* ArisePCStatus_007
* SaveData_ShortChat
* MenuSave
* SaveData_LongChat
* SaveData_ScenaioFlg - Not a typo this is the string from the executable
* SearchOwlSaveData
* TreasurePointSaveData
* SearchPointSaveData
* AriseMiningSaveData
* BreakPointSaveData
* MapGimmickSaveData
* OneTopSaveData
* QuestEnemyCountSaveData
* QuestSaveDataEx
* FishingSaveData
* CampPointSaveData
* EncountSymbolSaveData
* RecoveryPointSaveData

The `dump-save-offsets` command can be used to output to dump all save item sections offset locations within the decrypted file as well as the section size.  

## Integration into other tools/libraries.
The following list the methods that can be integrated to other tools to retrieve information about the save.
One use case for this is creating a save editor for the game
| Method | Description |
| --- | --- |
| `SaveDumpItemOffsetsArise.dump_save_section_offsets` | Static method: Invok to retrieve the list of save item offsets. Useful for implementing a save editor |
| `SaveDecryptArise.decrypt_save_buffer` | Static method: Invoke to decrypt an encrypted save|
| `SaveConvertAriseDecrypted.convert_decrypyted_save_header` | Static method: Invoke to convert a decrypted save between a source and target formats|
| `SaveEncryptArise.encrypt_save_buffer` | Static method: Invoke to encrypt a decrypted save |

All the methods above can be accessed by importing using the form:
 `from save_convert.tales_of.arise.tales_of_arise_save_converter import ...`

For a more in-depth list of save notes, the [Save_NOTES.md](./save_NOTES.md) can be examined.  

## Credits
This was all me baby!  
From reverse engineering the decryption function, to figuring out what the AES key for PC and PS5 saves are located as well as the XOR Cipher tables.
