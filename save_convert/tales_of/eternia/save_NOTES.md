# Tales of Eternia Remastered Save Decryption Notes
Contains notes found during the process of learning how to decrypt the PC Remastered save for Tales of Eternia

# Encryption Key Info
The save key is generated from a password of `1123581321345589` which is xor'ed with a byte string of `b"8D EF 02 2D 1B DF 05 5A A1 8E 0C C3 37 BE 0B B4"`.  
However the xor'ed password attempts to be decoded to a UTF-8 string which contains bytes that are out of the UTF-8 range and therefore relies on unicode
replacement character for code points that are out of range.  
See https://docs.python.org/3/library/codecs.html#codec-base-classes  
The salt string is `saltString` and both the xor'ed password and salt string is passed to the PBKDF2 key derivation function to create an AES an IV.  

### Remastered Save
The save slots repeat twice with a size 0x61840 (388424) bytes for a total save file size of 0xC3080 (798848).

The save data embeds a PNG at offset 0x1800 within each save slot.  

### Remastered listData.bin

The List data bin file seems to have the following format:
* 44 byte header `[0x, 0x2C)`
* 21 128-byte save entry sections starting at offset 0x2C (ex. `[0x2C, 0xAC)` for the first slot, `[0xAC, 0x12)` for the second slot, etc...)

Each save entry section repeats after the previous one until the end of the file.
