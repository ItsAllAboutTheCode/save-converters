The decompressed PS4 save has an extra 58400 bytes from the PC save.

# Steps to get save off PS4
Prereq: The PS4 needs to be to be jailbroken
1. Use the PS4 Apollo Save Tool to copy the decrypted save to a USB stick or the /data folder.
2. Copy user.dat file from the USB stick / use FTP to copy decrypyed save to computer.

# Steps to decompress save
Prereq: Need SenPatcher from https://github.com/AdmiralCurtiss/SenPatcher/releases
1. Use the SenPatcher to decompress 'Type 1' save.
   1. This can be done either using the SenPatcher GUI via the Toolbox menu or...
   1. Run the SenPatcher.exe(Windows) or sentools(Linux) on a CLI with the `Type1.Decompress` option
E.g `sentools Type1.Decompress <path-user.dat>`


*Note: PC Saves are stored in `%USERPROFILE%\Saved Games\Falcom\ed8`*

# Steps to modify PS4 save to load on PC.
Reminder that deleting bytes earlier in the file affects the offsets that are later in the file
1. Offset 0x0 - Append 4 bytes C0 08 07 00 - magic bytes to identify save
1. Offset 0x20 - Delete 20 bytes - Character data at offset 0x480 should be aligned now

1. Offset 0x2E24 - Delete 12 bytes - Should align location data for model 1
1. Offset 0x2E94 - Delete 8 bytes - Start partial alignment of animation state data for model 1
1. Offset 0x2EA8 - Delete 12 bytes
1. Offset 0x2FC8 - Delete 20 bytes
1. Offset 0x302C - Delete 8 bytes
1. Offset 0x3030 - Delete 4 bytes
1. Offset 0x30F0 - Delete 80 bytes
1. Offset 0x315C - Delete 12 bytes
1. Offset 0x3214 - Delete 80 bytes
1. Offset 0x3274 - Delete 8 bytes
1. Offset 0x3278 - Delete 4 bytes
1. Offset 0x3338 - Delete 80 bytes
1. Offset 0x33A4 - Delete 12 bytes - Finish alignment of animation state data for model 1

1. Offset (0x2D78 + 1760 * 1) = 0x3458 - Delete 72 bytes - Should align location data for model 2
1. Offset (0x2E94 + 1760 * 1) = 0x3574 - Delete 8 bytes - Start partial alignment of animatation state data for model 2
1. Offset (0x2EA8 + 1760 * 1) = 0x3588 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 1) = 0x36A8 - Delete 20 bytes
1. Offset (0x302C + 1760 * 1) = 0x370C - Delete 8 bytes
1. Offset (0x3030 + 1760 * 1) = 0x3710 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 1) = 0x37D0 - Delete 80 bytes
1. Offset (0x315C + 1760 * 1) = 0x383C - Delete 12 bytes
1. Offset (0x3214 + 1760 * 1) = 0x38F4 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 1) = 0x3954 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 1) = 0x3958 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 1) = 0x3A18 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 1) = 0x3A84 - Delete 12 bytes - Finish alignment of animation state data for model 2

1. Offset (0x2D78 + 1760 * 2) = 0x3B38 - Delete 72 bytes - Should align location data for model 3
1. Offset (0x2E94 + 1760 * 2) = 0x3C54 - Delete 8 bytes - Start partial alignment of animatation state data for model 3
1. Offset (0x2EA8 + 1760 * 2) = 0x3C68 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 2) = 0x3D88 - Delete 20 bytes
1. Offset (0x302C + 1760 * 2) = 0x3DEC - Delete 8 bytes
1. Offset (0x3030 + 1760 * 2) = 0x3DF0 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 2) = 0x3EB0 - Delete 80 bytes
1. Offset (0x315C + 1760 * 2) = 0x3F1C - Delete 12 bytes
1. Offset (0x3214 + 1760 * 2) = 0x3FD4 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 2) = 0x4034 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 2) = 0x4038 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 2) = 0x40F8 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 2) = 0x4164 - Delete 12 bytes - Finish alignment of animation state data for model 3

1. Offset (0x2D78 + 1760 * 3) = 0x4218 - Delete 72 bytes - Should align location data for model 4
1. Offset (0x2E94 + 1760 * 3) = 0x4334 - Delete 8 bytes - Start partial alignment of animatation state data for model 4
1. Offset (0x2EA8 + 1760 * 3) = 0x4348 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 3) = 0x4468 - Delete 20 bytes
1. Offset (0x302C + 1760 * 3) = 0x44CC - Delete 8 bytes
1. Offset (0x3030 + 1760 * 3) = 0x44D0 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 3) = 0x4590 - Delete 80 bytes
1. Offset (0x315C + 1760 * 3) = 0x45FC - Delete 12 bytes
1. Offset (0x3214 + 1760 * 3) = 0x46B4 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 3) = 0x4714 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 3) = 0x4718 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 3) = 0x47D8 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 3) = 0x4844 - Delete 12 bytes - Finish alignment of animation state data for model 4

1. Offset (0x2D78 + 1760 * 4) = 0x48F8 - Delete 72 bytes - Should align location data for model 5
1. Offset (0x2E94 + 1760 * 4) = 0x4A14 - Delete 8 bytes - Start partial alignment of animatation state data for model 5
1. Offset (0x2EA8 + 1760 * 4) = 0x4A28 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 4) = 0x4B48 - Delete 20 bytes
1. Offset (0x302C + 1760 * 4) = 0x4BAC - Delete 8 bytes
1. Offset (0x3030 + 1760 * 4) = 0x4BB0 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 4) = 0x4C70 - Delete 80 bytes
1. Offset (0x315C + 1760 * 4) = 0x4CDC - Delete 12 bytes
1. Offset (0x3214 + 1760 * 4) = 0x4D94 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 4) = 0x4DF4 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 4) = 0x4DF8 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 4) = 0x4EB8 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 4) = 0x4F24 - Delete 12 bytes - Finish alignment of animation state data for model 5

1. Offset (0x2D78 + 1760 * 5) = 0x4FD8 - Delete 72 bytes - Should align location data for model 6
1. Offset (0x2E94 + 1760 * 5) = 0x50F4 - Delete 8 bytes - Start partial alignment of animatation state data for model 6
1. Offset (0x2EA8 + 1760 * 5) = 0x5108 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 5) = 0x5228 - Delete 20 bytes
1. Offset (0x302C + 1760 * 5) = 0x528C - Delete 8 bytes
1. Offset (0x3030 + 1760 * 5) = 0x5290 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 5) = 0x5350 - Delete 80 bytes
1. Offset (0x315C + 1760 * 5) = 0x53BC - Delete 12 bytes
1. Offset (0x3214 + 1760 * 5) = 0x5474 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 5) = 0x54D4 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 5) = 0x54D8 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 5) = 0x5598 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 5) = 0x5604 - Delete 12 bytes - Finish alignment of animation state data for model 6

1. Offset (0x2D78 + 1760 * 6) = 0x56B8 - Delete 72 bytes - Should align location data for model 7
1. Offset (0x2E94 + 1760 * 6) = 0x57D4 - Delete 8 bytes - Start partial alignment of animatation state data for model 7
1. Offset (0x2EA8 + 1760 * 6) = 0x57E8 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 6) = 0x5908 - Delete 20 bytes
1. Offset (0x302C + 1760 * 6) = 0x596C - Delete 8 bytes
1. Offset (0x3030 + 1760 * 6) = 0x5970 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 6) = 0x5A30 - Delete 80 bytes
1. Offset (0x315C + 1760 * 6) = 0x5A9C - Delete 12 bytes
1. Offset (0x3214 + 1760 * 6) = 0x5B54 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 6) = 0x5BB4 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 6) = 0x5BB8 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 6) = 0x5C78 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 6) = 0x5CE4 - Delete 12 bytes - Finish alignment of animation state data for model 7

1. Offset (0x2D78 + 1760 * 7) = 0x5D98 - Delete 72 bytes - Should align location data for model 8
1. Offset (0x2E94 + 1760 * 7) = 0x5EB4 - Delete 8 bytes - Start partial alignment of animatation state data for model 8
1. Offset (0x2EA8 + 1760 * 7) = 0x5EC8 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 7) = 0x5FE8 - Delete 20 bytes
1. Offset (0x302C + 1760 * 7) = 0x604C - Delete 8 bytes
1. Offset (0x3030 + 1760 * 7) = 0x6050 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 7) = 0x6110 - Delete 80 bytes
1. Offset (0x315C + 1760 * 7) = 0x617C - Delete 12 bytes
1. Offset (0x3214 + 1760 * 7) = 0x6234 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 7) = 0x6294 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 7) = 0x6298 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 7) = 0x6358 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 7) = 0x63C4 - Delete 12 bytes - Finish alignment of animation state data for model 8

1. Offset (0x2D78 + 1760 * 8) = 0x6478 - Delete 72 bytes - Should align location data for model 9
1. Offset (0x2E94 + 1760 * 8) = 0x6594 - Delete 8 bytes - Start partial alignment of animatation state data for model 9
1. Offset (0x2EA8 + 1760 * 8) = 0x65A8 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 8) = 0x66C8 - Delete 20 bytes
1. Offset (0x302C + 1760 * 8) = 0x672C - Delete 8 bytes
1. Offset (0x3030 + 1760 * 8) = 0x6730 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 8) = 0x67F0 - Delete 80 bytes
1. Offset (0x315C + 1760 * 8) = 0x685C - Delete 12 bytes
1. Offset (0x3214 + 1760 * 8) = 0x6914 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 8) = 0x6974 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 8) = 0x6978 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 8) = 0x6A38 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 8) = 0x6AA4 - Delete 12 bytes - Finish alignment of animation state data for model 9

1. Offset (0x2D78 + 1760 * 9) = 0x6B58 - Delete 72 bytes - Should align location data for model 10
1. Offset (0x2E94 + 1760 * 9) = 0x6C74 - Delete 8 bytes - Start partial alignment of animatation state data for model 10
1. Offset (0x2EA8 + 1760 * 9) = 0x6C88 - Delete 12 bytes
1. Offset (0x2FC8 + 1760 * 9) = 0x6DA8 - Delete 20 bytes
1. Offset (0x302C + 1760 * 9) = 0x6E0C - Delete 8 bytes
1. Offset (0x3030 + 1760 * 9) = 0x6E10 - Delete 4 bytes
1. Offset (0x30F0 + 1760 * 9) = 0x6ED0 - Delete 80 bytes
1. Offset (0x315C + 1760 * 9) = 0x6F3C - Delete 12 bytes
1. Offset (0x3214 + 1760 * 9) = 0x6FF4 - Delete 80 bytes
1. Offset (0x3274 + 1760 * 9) = 0x7054 - Delete 8 bytes
1. Offset (0x3278 + 1760 * 9) = 0x7058 - Delete 4 bytes
1. Offset (0x3338 + 1760 * 9) = 0x7118 - Delete 80 bytes
1. Offset (0x33A4 + 1760 * 9) = 0x7184 - Delete 12 bytes - Finish alignment of animation state data for model 10

1. Offset 0x40C24 - Delete 53672 bytes - Inventory and game data at offset 0x40C24 should be aligned now
1. Offset 0x6B204 - Delete 764 bytes - Playtime at offset 0x6B748 should be aligned now.
1. Offset 0x708C0 - Delete 8 bytes - Makes the converted PS4 save have the exact size of an original PC Save

Total Bytes Changed PS4 -> PC:
First Model bytes changed = (12 + 8 + 12 + 20 + 8 + 4 + 80 + 12 + 80 + 8 + 4 + 80 + 12) = 340
Second thru Tenth Model bytes Changed = (**72** + 8 + 12 + 20 + 8 + 4 + 80 + 12 + 80 + 8 + 4 + 80 + 12) * 9 = (400 * 9) = 3600
Total = -4 + 20 + 340 + 3600 + 53672 + 764 + 8 = 58400 total bytes reduced.
After conversion the old PS4 save file should be the exact size of an original PC save.


## Additional Notes:
Mira offset = 0x65814
Sepith Mass offset = 0x657F0
Offset from PC to PS4 = +57628
Playtime is stored as a double at offset 0x6B748

Additional character models offset and animation data might not be correct past the first 7 characters(If there are more than 7 characters they are usually monsters or NPCs saved on the map).
Moving to a different map should resolve the issue.
The Animation data also looks like it serializes pointers as part of it's data.
As the PC version of Trails of Cold Steel 1/2 are 32-bit and the PS4 version are 64 bit, the PS4 save data is larger

### Character location/animation Data
The player location offset is critical align to make sure the player character spawns at the correct location after load.
That offset is at 0x2E24 in the PC version. It is made of 3 floats values for the X, Y, Z coordinates.
The stride of the data on PC appears to be 1760 bytes and on PS4 2160 bytes.
Therefore 400 bytes must be deleted from the PS4 save data for each character model to be aligned to the correct location.
The most important to align is the first as that is the player character. Any issues with NPC models or monsters being in the wrong location can be resolved by switching to different map zone

There appears to be a total of up to 10 character models stored in the save file, so for the purpose of getting the save to load correctly on the PC, adjusting the location data for the first 10 models is performed.

