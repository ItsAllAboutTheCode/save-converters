The decompressed PS4 save has an extra 2320 bytes from the PC save.

# Steps to get save off PS4
Prereq: The PS4 needs to be to be jailbroken
1. Use the PS4 Apollo Save Tool to copy the decrypted save to a USB stick or the /data folder.
2. Copy user.dat file from the USB stick / use FTP to copy decrypyed save to computer.

# Step to decompress save
Prereq: Need SenPatcher from https://github.com/AdmiralCurtiss/SenPatcher/releases
1. Use the SenPatcher to decompress 'Type 1' save.
   1. This can be done either using the SenPatcher GUI via the Tools section or...
   1. Run the SenPatcher.exe(Windows) or sentools(Linux) on a CLI with the `Type1.Decompress` option
E.g `sentools Type1.Decompress <path-user.dat>`


*Note: PC Saves are stored in `%USERPROFILE%\Saved Games\Falcom\ed8_psv3`*

# Steps to modify PS4 save to load on PC.
Reminder that deleting bytes earlier in the file affects the offsets that are later in the file
1. Offset 0xDE2C - Delete 16 bytes - Should align the location data for the player character 
1. Offset (0xDE2C + 1152 * 1) = 0xE2AC - Delete 16 bytes - Should align the location/animation state data for field model 2
1. Offset (0xDE2C + 1152 * 2) = 0xE27C - Delete 16 bytes - Should align the location/animation state data for field model 3
1. Offset (0xDE2C + 1152 * 3) = 0xEBAC - Delete 16 bytes - Should align the location/animation state data for field model 4
1. Offset (0xDE2C + 1152 * 4) = 0xF02C - Delete 16 bytes - Should align the location/animation state data for field model 5
1. Offset (0xDE2C + 1152 * 5) = 0xF4AC - Delete 16 bytes - Should align the location/animation state data for field model 6
1. Offset (0xDE2C + 1152 * 6) = 0xF92C - Delete 16 bytes - Should align the location/animation state data for field model 7
1. Offset (0xDE2C + 1152 * 6) = 0xFDAC - Delete 16 bytes - Should align the location/animation state data for field model 8
1. Offset (0xDE2C + 1152 * 6) = 0x1022C - Delete 16 bytes - Should align the location/animation state data for field model 9
1. Offset (0xDE2C + 1152 * 6) = 0x106AC - Delete 16 bytes - Should align the location/animation state data for field model 10
1. Offset 0x36580 - Delete 2176 bytes - Inventory data should be aligned
1. Offset 0x66980 - Append 16 bytes of FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 
1. Offset 0x66990 - Append another 16 bytes of FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 - Should align gameplay data such as Mira and Sepith
1. Offset 0x7840C - Delete 4 bytes - Should align what looks to be some kind of X, Y, Z coordinates
1. Offset 0x78440 - Delete 4 bytes - Should align the playtime data
1. Offset 0x1402C0 - Delete 8 bytes - Makes the converted save have the exact size of an original PC save

Total Bytes Changed PS4 -> PC = (16 * 10) + 2176 - (16 * 2) + (4 * 2) + 8 = 2320 total bytes reduced.
After conversion the old PS4 save file should have the same size as the original PC save.

## Additional Notes:
No 4 octer Magic byte to start the save data unlike Cold Steel 1 and Cold Steel 2 on PC
Mira offset = 0x676A8
Sepith Mass offset = 0x67664
Some kind Coordinate offset? = 0x7840C (3 floats)
Playtime (double type) offset = 0x78440
First Character location offset = 0xDE2C (stride between characters is 1152 bytes)

### Character location/animation Data
The player location offset is critical align to make sure the player character spawns at the correct location after load.
That offset is at 0xDE2C in the PC version. It is made of 3 floats values for the X, Y, Z coordinates.
The stride of the data on PC appears to be 1152 bytes and on PS4 1168 bytes.
Therefore 16 bytes must be deleted in the PC data for each character model to be aligned to the correct location.
The most important to align is the first as that is the player character. Any issues with NPC models or monsters being in the wrong location can be resolved by switching to different map zone

The field model location alignment is only done for the first 10 models in these notes. There could be more models on the map that need to be aligned.
However for the purpose of just getting the save to load correctly on the PC, adjusting the location data for the first 10 models should suffice.
Plus for each field model location that is fixed decreases the number of bytes that must be deleted in order to align the Gameplay data later on.

### Inventory Data
This is the offset that must be aligned for the save to load the inventory correctly.
It starts with the inventory data
Start Inventory Offset = 0x36580
First Item slot is for Team Balm: 2 bytes for the item ID (0x0 is Tear Balm, 0x1 is Teara Balm etc...). The next 2 bytes is the amount of that item in the inventory
