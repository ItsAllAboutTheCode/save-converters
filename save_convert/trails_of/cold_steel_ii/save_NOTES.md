The decompressed PS4 save has an extra 2904 bytes from the PC save.

# Steps to get save off PS4
Prereq: The PS4 needs to be to be jailbroken
1. Use the PS4 Apollo Save Tool to copy the decrypted save to a USB stick or the /data folder.
2. Copy user.dat file from the USB stick / use FTP to copy decrypyed save to computer.

# Steps to decompress save
Prereq: Need SenPatcher from https://github.com/AdmiralCurtiss/SenPatcher/releases
1. Use the SenPatcher to decompress 'Type 1' save.
   1. This can be done either using the SenPatcher GUI via the Toolbox menu or...
   1. Run the SenPatcher.exe(Windows) or sentools(Linux) on a CLI with the `Type1.Decompress` option.  
      E.g `sentools Type1.Decompress <path-user.dat>`


*Note: PC Saves are stored in `%USERPROFILE%\Saved Games\Falcom\ed8_2`*

# Steps to modify PS4 save to load on PC.
Reminder that deleting bytes earlier in the file affects the offsets that are later in the file
1. Offset 0x0 - Append 4 bytes 98 89 07 00 - magic bytes to identify save
1. Offset 0xCF2C - Delete 8 bytes - Should align the location data for the character model 1
1. Offset 0xCFAC - Delete 20 bytes - Should align the animation state data for character model 1
1. Offset (0xCFAC + 1148 * 1) = 0xD428 - Delete 8 bytes - Should align the location data for character model 2
1. Offset (0xCFC0 + 1148 * 1) = 0xD43C - Delete 12 bytes - Should align the animation state data for character model 2
1. Offset (0xCFAC + 1148 * 2) = 0xD8A4 - Delete 8 bytes - Should align the location data for character model 3
1. Offset (0xCFC0 + 1148 * 2) = 0xD8B8 - Delete 12 bytes - Should align the animation state data for character model 3
1. Offset (0xCFAC + 1148 * 3) = 0xDD20 - Delete 8 bytes - Should align the location data for character model 4
1. Offset (0xCFC0 + 1148 * 3) = 0xDD34 - Delete 12 bytes - Should align the animation state data for character model 4
1. Offset (0xCFAC + 1148 * 4) = 0xE19C - Delete 8 bytes - Should align the location data for character model 5
1. Offset (0xCFC0 + 1148 * 4) = 0xE1B0 - Delete 12 bytes - Should align the animation state data for character model 5
1. Offset (0xCFAC + 1148 * 5) = 0xE618 - Delete 8 bytes - Should align the location data for character model 6
1. Offset (0xCFC0 + 1148 * 5) = 0xE62C - Delete 12 bytes - Should align the animation state data for character model 6
1. Offset (0xCFAC + 1148 * 6) = 0xEA94 - Delete 8 bytes - Should align the location data for character model 7
1. Offset (0xCFC0 + 1148 * 6) = 0xEAA8 - Delete 12 bytes - Should align the animation state data for character model 7
1. Offset (0xCFAC + 1148 * 7) = 0xEF10 - Delete 8 bytes - Should align the location data for character model 8
1. Offset (0xCFC0 + 1148 * 7) = 0xEF24 - Delete 12 bytes - Should align the animation state data for character model 8
1. Offset (0xCFAC + 1148 * 8) = 0xF38C - Delete 8 bytes - Should align the location data for character model 9
1. Offset (0xCFC0 + 1148 * 8) = 0xF3A0 - Delete 12 bytes - Should align the animation state data for character model 9
1. Offset (0xCFAC + 1148 * 9) = 0xF808 - Delete 8 bytes - Should align the location data for character model 10
1. Offset (0xCFC0 + 1148 * 9) = 0xF81C - Delete 12 bytes - Should align the animation state data for character model 10
1. Offset (0xCFAC + 1148 * 10) = 0xFC84 - Delete 8 bytes - Should align the location data for character model 11
1. Offset (0xCFC0 + 1148 * 10) = 0xFC98 - Delete 12 bytes - Should align the animation state data for character model 11
1. Offset (0xCFAC + 1148 * 11) = 0x10100 - Delete 8 bytes - Should align the location data for character model 12
1. Offset (0xCFC0 + 1148 * 11) = 0x10114 - Delete 12 bytes - Should align the animation state data for character model 12
1. Offset (0xCFAC + 1148 * 12) = 0x1057C - Delete 8 bytes - Should align the location data for character model 13
1. Offset (0xCFC0 + 1148 * 12) = 0x10590 - Delete 12 bytes - Should align the animation state data for character model 13
1. Offset (0xCFAC + 1148 * 13) = 0x109F8 - Delete 8 bytes - Should align the location data for character model 14
1. Offset (0xCFC0 + 1148 * 13) = 0x10A0C - Delete 12 bytes - Should align the animation state data for character model 14
1. Offset (0xCFAC + 1148 * 14) = 0x10E74 - Delete 8 bytes - Should align the location data for character model 15
1. Offset (0xCFC0 + 1148 * 14) = 0x10E88 - Delete 12 bytes - Should align the animation state data for character model 15
1. Offset (0xCFAC + 1148 * 15) = 0x112F0 - Delete 8 bytes - Should align the location data for character model 16
1. Offset (0xCFC0 + 1148 * 15) = 0x11304 - Delete 12 bytes - Should align the animation state data for character model 16
1. Offset (0xCFAC + 1148 * 16) = 0x1176C - Delete 8 bytes - Should align the location data for character model 17
1. Offset (0xCFC0 + 1148 * 16) = 0x11780 - Delete 12 bytes - Should align the animation state data for character model 17
1. Offset (0xCFAC + 1148 * 17) = 0x11BE8 - Delete 8 bytes - Should align the location data for character model 18
1. Offset (0xCFC0 + 1148 * 17) = 0x11BFC - Delete 12 bytes - Should align the animation state data for character model 18
1. Offset (0xCFAC + 1148 * 18) = 0x12064 - Delete 8 bytes - Should align the location data for character model 19
1. Offset (0xCFC0 + 1148 * 18) = 0x12078 - Delete 12 bytes - Should align the animation state data for character model 19
1. Offset (0xCFAC + 1148 * 19) = 0x124E0 - Delete 8 bytes - Should align the location data for character model 20
1. Offset (0xCFC0 + 1148 * 19) = 0x124F4 - Delete 12 bytes - Should align the animation state data for character model 20
1. Offset (0xCFAC + 1148 * 20) = 0x1295C - Delete 8 bytes - Should align the location data for character model 21
1. Offset (0xCFC0 + 1148 * 20) = 0x12970 - Delete 12 bytes - Should align the animation state data for character model 21
1. Offset (0xCFAC + 1148 * 21) = 0x12DD8 - Delete 8 bytes - Should align the location data for character model 22
1. Offset (0xCFC0 + 1148 * 21) = 0x12DEC - Delete 12 bytes - Should align the animation state data for character model 22
1. Offset (0xCFAC + 1148 * 22) = 0x13254 - Delete 8 bytes - Should align the location data for character model 23
1. Offset (0xCFC0 + 1148 * 22) = 0x13268 - Delete 12 bytes - Should align the animation state data for character model 23
1. Offset (0xCFAC + 1148 * 23) = 0x136D0 - Delete 8 bytes - Should align the location data for character model 24
1. Offset (0xCFC0 + 1148 * 23) = 0x136E4 - Delete 12 bytes - Should align the animation state data for character model 24
1. Offset (0xCFAC + 1148 * 24) = 0x13B4C - Delete 8 bytes - Should align the location data for character model 25
1. Offset (0xCFC0 + 1148 * 24) = 0x13B60 - Delete 12 bytes - Should align the animation state data for character model 25
1. Offset (0xCFAC + 1148 * 25) = 0x13FC8 - Delete 8 bytes - Should align the location data for character model 26
1. Offset (0xCFC0 + 1148 * 25) = 0x13FDC - Delete 12 bytes - Should align the animation state data for character model 26
1. Offset (0xCFAC + 1148 * 26) = 0x14444 - Delete 8 bytes - Should align the location data for character model 27
1. Offset (0xCFC0 + 1148 * 26) = 0x14458 - Delete 12 bytes - Should align the animation state data for character model 27
1. Offset (0xCFAC + 1148 * 27) = 0x148C0 - Delete 8 bytes - Should align the location data for character model 28
1. Offset (0xCFC0 + 1148 * 27) = 0x148D4 - Delete 12 bytes - Should align the animation state data for character model 28

1. Offset 0x354EC - Delete 2320 bytes - Game data should be aligned
1. Offset 0x70BDC - Delete 12 bytes - Playtime at offset 0x71208 should be aligned
1. Offset 0x78998 - Delete 8 bytes - Makes the PS4 and PC save have the exact same size

Total Bytes Changed PS4 -> PC:  
First thru Tenth Model bytes Changed = (20 * 27) = 540  
Total = -4 + 8 + 20 + 540 + 2320 + 12 + 8 = 2904 total bytes reduced.  
After conversion the old PS4 save file should have the same size as the original PC save.  

## Additional Notes:
After modifications PC save offsets:  
Inventory start offset = 0x354EC  
Mira offset = 0x661D4  
Sepith Mass offset = 0x661B0  
Playtime (double type) offset = 0x71208  
First Character location offset = 0xCF2C (stride between characters is 1148 bytes)  

### Character location/animation Data
The player location offset is critical to align to make sure the player character spawns at the correct location after load.  
That offset is at 0xCF2C in the PC version. It is made of 3 floats values for the X, Y, Z coordinates.  
The stride of the data on PC appears to be 1148 bytes and on PS4 1168 bytes.  
Therefore 20 bytes must be deleted from the PS4 save data for each character model to be aligned to the correct location.  
The most important to align is the first model as that is normally the player character. Any issues with NPC models or monsters being in the wrong location can be resolved by switching to different map zone.  

