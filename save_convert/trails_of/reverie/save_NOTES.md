# Key Notes
The Trails of Reverie save on PS4 is compressed using the Falcom Type1 Decompression algorithm
However on PC the save is compressed ZSTD using
The decompressed PS4 save = 1,724,096
The decompressed PC save =  1,720,032

The decompressed PS4 has an extra 4064 bytes.

# Steps to get save off PS4
Prereq: The PS4 needs to be to be jailbroken
1. Use the PS4 Apollo Save Tool to copy the decrypted save to a USB stick or the /data folder.
2. Copy user.dat file from the USB stick / use FTP to copy decrypyed save to computer.

# Step to decompress PS4 save
Prereq: Need SenPatcher from https://github.com/AdmiralCurtiss/SenPatcher/releases
1. Use the SenPatcher to decompress 'Type 1' save.
   1. This can be done either using the SenPatcher GUI via the Tools section or...
   1. Run the SenPatcher.exe(Windows) or sentools(Linux) on a CLI with the `Type1.Decompress` option
E.g `sentools Type1.Decompress <path-user.dat>`


*Note: PC Saves are stored in `%USERPROFILE%\Saved Games\Falcom\ed8_psv5`*  
*Also PC saves are compressed using ZStandard, however the PC version can load uncompressed saves*

# Steps to modify PS4 save to load on PC.
Reminder that deleting bytes earlier in the file affects the offsets that are later in the file
1. Offset 0x18204 - Delete 12 bytes - Aligns coordinate data for model 1
1. Offset 0x182E8 - Delete 16 bytes - Aligns animation data for model 1
1. Offset (0x18204 + 932 * 1) =  0x185A8 - Delete 12 bytes - Partially aligns data for model 2
1. Offset (0x182E8 + 932 * 1) =  0x1868C - Delete 16 bytes - Completes alignment of data for model 2
1. Offset (0x18204 + 932 * 2) =  0x1894C - Delete 12 bytes - Partially aligns data for model 3
1. Offset (0x182E8 + 932 * 2) =  0x18A30 - Delete 16 bytes - Completes alignment of data for model 3
1. Offset (0x18204 + 932 * 3) =  0x18CF0 - Delete 12 bytes - Partially aligns data for model 4
1. Offset (0x182E8 + 932 * 3) =  0x18DD4 - Delete 16 bytes - Completes alignment of data for model 4
1. Offset (0x18204 + 932 * 4) =  0x19094 - Delete 12 bytes - Partially aligns data for model 5
1. Offset (0x182E8 + 932 * 4) =  0x19178 - Delete 16 bytes - Completes alignment of data for model 5
1. Offset (0x18204 + 932 * 5) =  0x19438 - Delete 12 bytes - Partially aligns data for model 6
1. Offset (0x182E8 + 932 * 5) =  0x1951C - Delete 16 bytes - Completes alignment of data for model 6
1. Offset (0x18204 + 932 * 6) =  0x197DC - Delete 12 bytes - Partially aligns data for model 7
1. Offset (0x182E8 + 932 * 6) =  0x198C0 - Delete 16 bytes - Completes alignment of data for model 7
1. Offset (0x18204 + 932 * 7) =  0x19B80 - Delete 12 bytes - Partially aligns data for model 8
1. Offset (0x182E8 + 932 * 7) =  0x19C64 - Delete 16 bytes - Completes alignment of data for model 8
1. Offset (0x18204 + 932 * 8) =  0x19F24 - Delete 12 bytes - Partially aligns data for model 9
1. Offset (0x182E8 + 932 * 8) =  0x1A008 - Delete 16 bytes - Completes alignment of data for model 9
1. Offset (0x18204 + 932 * 9) =  0x1A2C8 - Delete 12 bytes - Partially aligns data for model 10
1. Offset (0x182E8 + 932 * 9) =  0x1A3AC - Delete 16 bytes - Completes alignment of data for model 10
1. Offset (0x18204 + 932 * 10) = 0x1A66C - Delete 12 bytes - Partially aligns data for model 11
1. Offset (0x182E8 + 932 * 10) = 0x1A750 - Delete 16 bytes - Completes alignment of data for model 11
1. Offset (0x18204 + 932 * 11) = 0x1AA10 - Delete 12 bytes - Partially aligns data for model 12
1. Offset (0x182E8 + 932 * 11) = 0x1AAF4 - Delete 16 bytes - Completes alignment of data for model 12
1. Offset (0x18204 + 932 * 12) = 0x1ADB4 - Delete 12 bytes - Partially aligns data for model 13
1. Offset (0x182E8 + 932 * 12) = 0x1AE98 - Delete 16 bytes - Completes alignment of data for model 13
1. Offset (0x18204 + 932 * 13) = 0x1B158 - Delete 12 bytes - Partially aligns data for model 14
1. Offset (0x182E8 + 932 * 13) = 0x1B23C - Delete 16 bytes - Completes alignment of data for model 14
1. Offset (0x18204 + 932 * 14) = 0x1B4FC - Delete 12 bytes - Partially aligns data for model 15
1. Offset (0x182E8 + 932 * 14) = 0x1B5E0 - Delete 16 bytes - Completes alignment of data for model 15
1. Offset (0x18204 + 932 * 15) = 0x1B8A0 - Delete 12 bytes - Partially aligns data for model 16
1. Offset (0x182E8 + 932 * 15) = 0x1B984 - Delete 16 bytes - Completes alignment of data for model 16
1. Offset (0x18204 + 932 * 16) = 0x1BC44 - Delete 12 bytes - Partially aligns data for model 17
1. Offset (0x182E8 + 932 * 16) = 0x1BD28 - Delete 16 bytes - Completes alignment of data for model 17
1. Offset (0x18204 + 932 * 17) = 0x1BFE8 - Delete 12 bytes - Partially aligns data for model 18
1. Offset (0x182E8 + 932 * 17) = 0x1C0CC - Delete 16 bytes - Completes alignment of data for model 18
1. Offset 0x38E84 - Delete 3540 bytes - Aligns the Inventory data
1. Offset 0x94E78 - Delete 12 bytes - Aligns the Playtime data
1. Offset 0x1A3EE0 - Delete 8 bytes - Deletes the final 8 bytes of the file to have filesize match the PC filesize of 1720032

Total Bytes Changed PS4 -> PC = (28 * 18) + 3540 + 12 + 8 = 4064 total bytes reduced.
Total difference between PS4 and PC is 0 bytes in size.

# Steps to Fix save checksum or ignore it
## Fixing Checksum with SenPatcher
The SenPatcher application can be used to fix the save checksum:
1. Use the SenPatcher to Fix Checksum of CS4 or Reverie Save.
1. Alternatively the checksum can be fixed by running the SenPatcher.exe(Windows) or sentools(Linux) on a CLI with the `Save.Checksum.Fix` option
E.g `sentools Save.Checksum.Fix <path-user.dat>`

## Ignore the Checksum
Ignoring the Checksum can be done by either patching the `hnk.exe` executable or by using Cheat Engine application to apply the cheat table to skip over the checksum check.

### Address Notes
Within the save file the checksum is located at offset 0xC for Trails into Reverie (for other games such as Horizon this is 0x8).
This checksum is calculated by running a CRC-32 algorithm with a polynomial of 0xEDB88320 from bytes 0x10 to the end of the save file.

0x97D680 Address within the executable where the CRC-32 checksum function starts
```
cmp     dword ptr [rip + 0xd2252d], 0
lea     r11, [rip + 0xd22522]
mov     r10d, r8d
mov     r9d, edx
jne     0x97d73c
xor     edx, edx
mov     r8, r11
nop     
mov     ecx, edx
lea     r8, [r8 + 4]
and     ecx, 1
mov     eax, edx
shr     eax, 1
neg     ecx
and     ecx, 0xedb88320
inc     edx
xor     ecx, eax
mov     eax, ecx
shr     ecx, 1
and     eax, 1
neg     eax
and     eax, 0xedb88320
xor     eax, ecx
mov     ecx, eax
shr     eax, 1
and     ecx, 1
neg     ecx
and     ecx, 0xedb88320
xor     ecx, eax
mov     eax, ecx
shr     ecx, 1
and     eax, 1
neg     eax
and     eax, 0xedb88320
xor     eax, ecx
mov     ecx, eax
shr     eax, 1
and     ecx, 1
neg     ecx
and     ecx, 0xedb88320
xor     ecx, eax
mov     eax, ecx
shr     ecx, 1
and     eax, 1
neg     eax
and     eax, 0xedb88320
xor     eax, ecx
mov     ecx, eax
shr     eax, 1
and     ecx, 1
neg     ecx
and     ecx, 0xedb88320
xor     ecx, eax
mov     eax, ecx
shr     ecx, 1
and     eax, 1
neg     eax
and     eax, 0xedb88320
xor     eax, ecx
mov     dword ptr [r8 - 4], eax
cmp     edx, 0x100
jb      0x97d6a0
lea     r8, [rip + 0x3568f9]
not     r10d
mov     eax, r10d
test    r9d, r9d
jle     0x97d76e
nop     
movzx   ecx, byte ptr [r8]
lea     r8, [r8 + 1]
movzx   edx, al
xor     rdx, rcx
shr     eax, 8
xor     eax, dword ptr [r11 + rdx*4]
sub     r9d, 1
jne     0x97d750
not     eax
ret     
lea     r8, [rip + 0x3568c8]
mov     r9b, 0x52
cmp     r9b, 0x23
jne     0x97d78b
cmp     byte ptr [r8], r9b
jne     0x97d78b
cmp     byte ptr [r8 + 1], r9b
cmove   eax, r10d
movzx   edx, al
movzx   ecx, r9b
movzx   r9d, byte ptr [r8]
xor     rdx, rcx
shr     eax, 8
inc     r8
xor     eax, dword ptr [r11 + rdx*4]
test    r9b, r9b
jne     0x97d778
not     eax
ret
```

### Patching the Executable
In version 1.1.4, the executable can be patched at the offset 0x59C66E.
The following hex pattern can be used to is 41 39 52 0C 74 04 locate the bytes to patch in other versions of the game.
Those bytes need to be replaced with 41 39 52 0C **EB** 04.
This patches the `je` (74) instruction to be `jmp` (EB).


## Additional Notes:
No Magic byte sequence to start the save data unlike Cold Steel 1 and Cold Steel 2 on PC
Mira offset = 0x80C08
Sepith Mass offset = 0x80B84
Playtime (double type) offset = 0x95AB0
First Character location offset = 0x18204 (stride between characters is 932 bytes)

### Character location/animation Data
The player location offset is critical align to make sure the player character spawns at the correct location after load.
It appears there are three set of offsets that have the same value They are made of 3 floats values for the X, Y, Z coordinates.
Their offsets 0x18204, 0x18244, 0x18254 in the PC Version
The stride of the data on PC appears to be 932 bytes and on PS4 960 bytes.
Therefore 28 bytes must be deleted in the PC data for each character model to be aligned to the correct location.
The most important to align is the first as that is the player character. Any issues with NPC models or monsters being in the wrong location can be resolved by switching to different map zone

The field model location alignment is only done for the first 10 models in these notes. There could be more models on the map that need to be aligned.
However for the purpose of just getting the save to load correctly on the PC, adjusting the location data for the first 18 models should suffice.
Plus for each field model location that is fixed decreases the number of bytes that must be deleted in order to align the Gameplay data later on.

###  Inventory Data
This is the offset that must be aligned for the save to load the inventory correctly.
Start Inventory Offset = 0x38E84 
First Item slot is for Team Balm: 2 bytes for the item ID (0x0 is Tear Balm, 0x1 is Teara Balm etc...).  The stride of the data appears to be 32 bytes between entries
