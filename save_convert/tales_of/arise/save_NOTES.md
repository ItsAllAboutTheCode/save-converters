# Tales of Arise Decyption Notes
Contains notes found during the process to learn how to decrypt Tales of Arise save
## Save File Offsets
* 0x32058 - Where save data section begins.
* 0x32058 - Magic Byte which identifies save data. Has value 30 16 05 10  
* 0x3205C - Size of the encrypted Save Data save section:  
          For Base Game Save = 0x87BC0  
          For DLC Game Save = 0x5EC60  
* 0x32060 - 20 Byte sha1 hash of save data: Starts at offset 0x32078 (where the first save block starts)  
* 0x32068 - 2 byte sequence - The first byte indicates if XOR cipher should be performed for the platform  
  * The second byte is used to determine the alternate XOR logic to use, however that byte is always 0x1 on PC/PS5.  
  Also the alternate XOR logic is the same as the original logic.  
  For PS5 the bytes are set set to 03 01  
  For PC the bytes are set to 00 01
  * If the first byte is 0x00 on PC, then the XOR logic is performed
  * If the first byte is 0x03 on PS5, then the XOR logic is performed
* 0x3206A - 2 byte padding to get to 4-byte alignment
* 0x32078 - Start of encrypted save data

### For Base Game Save Only
* 0xB9C18 - End of decrypted data - Save file size is 760,856
### For DLC Save Only
* 0x90CB8 - End of decrypted data - Save file size is 593,080

For the byte tha indicates whether XOR should be performed.  
If the byte at offset 0x32068 is not set to the specified, then XOR cipher is skipped when performing saving/loading on that platform
Right now, known values are:  
| Byte Value | Platform |
| --- | --- |
| 0x0 | PC |
| 0x1 | Unknown |
| 0x2 | Unknown |
| 0x3 | PS5 

I am assuming other platforms occupy bytes 01 and 02.  
Maybe the other values are variants of PS4, Xbox One, Xbox Series X.
It is important that the value is correct for the save the platform is expected to load for.  
Otherwise the XOR cipher against the AES decrypted data would fail and the save load logic would raise an exception.  

### Executable Information
    
At address 0x332C740 in Tales of Arise.exe is a AES-256 ECB cipher key for decryption of save data.  

Memory address to Executable offset:  
Take the memory address, striping the leading 14 from the address and subtract 0x1200 hex to get the offset in the executable file.  


## Debugging PC Save Encryption / Decryption
The PC Encryption Decyption algorithm was studied using the following Tales of Arise Steam Build:
```
Game menu:  1.8.0.0
Patchnotes: -
SteamDB:    build 12823607 from 12 December 2023
```

All the offsets are based on that build of the executable

PC Save Decryption starts at instruction 0x1408DA449  
PC Save Encryption starts at instruction 0x1408D9E22  

Executable offset on PC 0x1408DA11C points references the bytes that are written for the X0R cipher.  
The value is a constant 0x100 hex which writes bytes 00 01 to the save, which indicates that save data underwent an XOR cipher before AES encryption.

The encryption section is marked by the read of the Cipher Key at .text section 0x14332D340
which corresponds to 0x332C740 in the Tales of Arise.exe

## PS5 Save Key Research
During Research for Save Keys, the following list
of bytes came up as potential PS5 keys:  
`9QLJPHXZUnG2LJAHXC6wcfHYkBVzSHyB`  
`JEExTp59i6QP_pg2GK7ZjcW32bJ-XmRW`  
`-53t9cPfnriPcJ-kKcrRaCb6BriUScd`  
`CXYAXC4YcGMRuRRjBh_D7Ts8MPkZ4G9`  

The actual save keys and XOR tables are listed in the next section.  

## Save Keys and XOR Cipher Tables
### PC AES Save Key
Located at 0x332C740 in Tale of Arise.exe  
First 32-bytes are cipher key for AES-256 ECB  
```python
# b'fgEQ5GbxFXp-mD6tHTZVmiWwgK8PwgK5MfcnGHurirrJY9xVxkd8i-Vy3LD6Rhx\x00'
bytes.fromhex(
    "66674551354762784658702D6D443674"  
    "48545A566D695777674B385077674B35"  
    "4D66636E474875726972724A59397856"  
    "786B6438692D5679334C443652687800"
)
```

### PC XOR Cipher Table
64 byte table which is xor'ed with the AES decrypted result to get the decrypted save data.  
Located at 0x332C780 in Tale of Arise.exe  
```python
# b'NjFnSJsNQpiMrnQegcBr5AgrZAGA5gRMkCADNMZR3izEWVR3ZicicXZNsFyKUmr\x00'
bytes.fromhex(
    "4E6A466E534A734E5170694D726E5165" 
    "67634272354167725A4147413567524D"
    "6B4341444E4D5A5233697A4557565233"
    "5A69636963585A4E7346794B556D7200"
)
```

### PS5 AES Save Key
```python
# b'9QLJPHXZUnG2LJAHXC6wcfHYkBVzSHyB-53t9cPfnriPcJ-kKcrRaCb6BriUScd\x00'
bytes.fromhex(
    "39514C4A5048585A556E47324C4A4148"
    "58433677636648596B42567A53487942"
    "2D353374396350666E726950634A2D6B"
    "4B637252614362364272695553636400"
)
```

### PS5 XOR Cipher Table
```python
# b'JEExTp59i6QP_pg2GK7ZjcW32bJ-XmRWCXYAXC4YcGMRuRRjBh_D7Ts8MPkZ4G9\x00'
bytes.fromhex(
    "4A45457854703539693651505F706732" # JEExTp59i6QP_pg2GK7ZjcW32bJ-XmRW
    "474B375A6A63573332624A2D586D5257"
    "435859415843345963474D527552526A"
    "42685F44375473384D506B5A34473900"
)
```

Eboot.bin offset 0x56D3BF6 looks like the save routine encrypt call

The following code is what was used to find the XOR Cipher table
After testing out the potential cipher keys

```python
# NOTE: The PS5 encryption key and XOR table was found this function
def find_ps5_xor_table_candidates(candidate_ps5_cipher_keys: list[bytes] = [ps5_cipher_key]):
    # Read the decrypted boot file into memory
    eboot_path = Path("/mnt/DataDrive/Hacking/Sony/PS5/Debugging/eboot.bin")
    eboot_buffer = b""
    with eboot_path.open("rb") as eboot_file:
        eboot_buffer = eboot_file.read()
    for cipher_key in candidate_ps5_cipher_keys:
        cipher = AES.new(cipher_key[:32], mode=AES.MODE_ECB)
        xored_buffer = bytearray(len(encrypted_ps5_test_buffer))
        cipher.decrypt(encrypted_ps5_test_buffer, output=xored_buffer)

        # After the decryption of the first 64-byte block, the Tales of Arise
        # save contains offsets to other save items within the save file
        # the high byte offset is always 0x00.
        # This is based at looking at the decrypted block on PC
        # Therefore perform a regex search of <3-of-any-bytes> 00 <3-of-any-bytes> 00 <3-of-any-bytes> 00
        # That should return a list of potential xor
        max_bytes_to_match = 12
        check_for_zero_every_multiple_4 = re.compile(
            b"".join(
                [
                    rb".{3}" + re.escape(xored_buffer[i + 3].to_bytes())
                    for i in range(0, min(len(xored_buffer), max_bytes_to_match), 4)
                ]
            )
        )
        if match_results := check_for_zero_every_multiple_4.findall(eboot_buffer):
            print(
                f"After decryption using key={cipher_key.hex()},"
                " The following offsets in the eboot.bin are potential xor table candidates:\n"
                + f"{'\n'.join([str(match_result) for match_result in match_results])}"
            )
            pretty_print_hex(xored_buffer)

```


## Save Item Section
The following save sections are stored in the save data a seemingly random order.  
After decryption of the first 64-bite save block at offset 0x32078, that block at the location is a list.  
16 4-byte little endian offsets into the save data block.  
### For PC Saves
The 10th 4-byte entry (10 * 4 = 40 = 0x28) that is at offset (0x32078 + 0x28) = 0x320A0 is the offset (zero-based).  
### For PS5 Saves
The 6th 4-byte entry (6 * 4 = 24 = 0x18) that is at offset (0x32078 + 0x18) = 0x32000 is the offset (zero-based).  

That points to the table that contains the number of Save Item sections (30 or 0x1E) and the address to the save item section to load.  
After the first Save Item section is loaded, it contains a pointer to the next save order section to load.  
Again, this order is not fixed and will change every time the game is saved.  

Therefore if anyone wants to make a save editor for this game, they would need to parse save item sections in that order.  

All the offsets are the save data block at 0x32058  

### Save Item Sections are as follows:
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


### Convert between Decrypted PS5 and PC save
To convert a decrypted PS5 to decrypted PC save and vice versa, all that needs to be done is to swap the DWORD(4-bytes) at offset 0x32090 with 0x320A0.  
Once those bytes have been swapped, they can be encrypted using the AES save key for that platform.
