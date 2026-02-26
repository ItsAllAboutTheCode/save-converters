The decompressed PS4 save has an extra 2328 bytes from the PC save.

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


*Note: PC Saves are stored in `%USERPROFILE%\Saved Games\Falcom\ed8_psv4`*

# Steps to modify PS4 save to load on PC.
Reminder that deleting bytes earlier in the file affects the offsets that are later in the file
1. Offset 0x152DC - Delete 4 bytes - Aligns coordinate data for model 1
1. Offset 0x153A0 - Delete 16 bytes - Aligns animation data for model 1
1. Offset (0x153A0 + 960 * 1) = 0x15760 - Delete 16 bytes - Aligns the location/animation data for model 2
1. Offset (0x153A0 + 960 * 2) = 0x15B20 - Delete 16 bytes - Aligns the location/animation data for model 3
1. Offset (0x153A0 + 960 * 3) = 0x15EE0 - Delete 16 bytes - Aligns the location/animation data for model 4
1. Offset (0x153A0 + 960 * 4) = 0x162A0 - Delete 16 bytes - Aligns the location/animation data for model 5
1. Offset (0x153A0 + 960 * 5) = 0x16660 - Delete 16 bytes - Aligns the location/animation data for model 6
1. Offset (0x153A0 + 960 * 6) = 0x16A20 - Delete 16 bytes - Aligns the location/animation data for model 7
1. Offset (0x153A0 + 960 * 7) = 0x16DE0 - Delete 16 bytes - Aligns the location/animation data for model 8
1. Offset (0x153A0 + 960 * 8) = 0x171A0 - Delete 16 bytes - Aligns the location/animation data for model 9
1. Offset (0x153A0 + 960 * 9) = 0x17560 - Delete 16 bytes - Aligns the location/animation data for model 10
1. Offset (0x153A0 + 960 * 10) = 0x17920 - Delete 16 bytes - Aligns the location/animation data for model 11
1. Offset (0x153A0 + 960 * 11) = 0x17CE0 - Delete 16 bytes - Aligns the location/animation data for model 12
1. Offset (0x153A0 + 960 * 12) = 0x180A0 - Delete 16 bytes - Aligns the location/animation data for model 13
1. Offset (0x153A0 + 960 * 13) = 0x18460 - Delete 16 bytes - Aligns the location/animation data for model 14
1. Offset (0x153A0 + 960 * 14) = 0x18820 - Delete 16 bytes - Aligns the location/animation data for model 15
1. Offset (0x153A0 + 960 * 15) = 0x18BE0 - Delete 16 bytes - Aligns the location/animation data for model 16
1. Offset (0x153A0 + 960 * 16) = 0x18FA0 - Delete 16 bytes - Aligns the location/animation data for model 17
1. Offset (0x153A0 + 960 * 17) = 0x19360 - Delete 16 bytes - Aligns the location/animation data for model 18
1. Offset 0x36F1C - Delete 2016 bytes - Aligns the Inventory data
1. Offset 0x7CA20 - Delete 12 bytes - Aligns the Playtime data
1. Offset 0x1656A8 - Delete 8 bytes - Deletes the final 8 bytes of the file to have filesize match the PC filesize of 1463976

Total Bytes Changed PS4 -> PC = 4 + (16 * 18) + 2016 + 12 + 8 = 2328 total bytes reduced.
Total difference between PS4 and PC is 0 bytes in size.

# Steps to Fix save checksum or ignore it
## Fixing Checksum with SenPatcher
The SenPatcher application can be used to fix the save checksum:
1. Use the SenPatcher to Fix Checksum of CS4 or Reverie Save.
1. Alternatively the checksum can be fixed by running the SenPatcher.exe(Windows) or sentools(Linux) on a CLI with the `Save.Checksum.Fix` option
E.g `sentools Save.Checksum.Fix <path-user.dat>`

## Ignore the Checksum
Ignoring the Checksum can be done by either patching the `ed8_4_PC.exe` executable or by using Cheat Engine application to apply the cheat table to skip over the checksum check.

### Address Notes
Within the save file the checksum is located at offset 0xC for Trails of Cold Steel IV (for other games such as Horizon this is 0x8).
This checksum is calculated by running a CRC-32 algorithm with a polynomial of 0xEDB88320 from bytes 0x10 to the end of the save file.

0x7184B0 Address within the executable where the CRC-32 checksum function starts
```
push    rdi
cmp     dword ptr [rip + 0x307ba3b], 0
lea     rdi, [rip + 0x307ba30]
mov     r11d, r8d
mov     r9d, edx
mov     r10, rcx
jne     0x718588
mov     qword ptr [rsp + 0x10], rbx
xor     edx, edx
mov     rbx, rdi
nop     dword ptr [rax]
mov     r8d, edx
lea     rbx, [rbx + 4]
and     r8d, 1
mov     eax, edx
shr     eax, 1
neg     r8d
and     r8d, 0xedb88320
inc     edx
xor     r8d, eax
mov     eax, r8d
shr     r8d, 1
and     eax, 1
neg     eax
and     eax, 0xedb88320
xor     eax, r8d
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
mov     dword ptr [rbx - 4], eax
cmp     edx, 0x100
jb      0x7184e0
mov     rbx, qword ptr [rsp + 0x10]
not     r11d
mov     eax, r11d
test    r9d, r9d
jle     0x7185c2
nop     dword ptr [rax]
nop     word ptr [rax + rax]
movzx   ecx, byte ptr [r10]
lea     r10, [r10 + 1]
movzx   edx, al
xor     rdx, rcx
mov     ecx, eax
shr     ecx, 8
mov     eax, dword ptr [rdi + rdx*4]
xor     eax, ecx
sub     r9d, 1
jne     0x7185a0
not     eax
pop     rdi
ret     
```

### Patching the Executable
In version 1.2.1, the executable can be patched at the offset 0x3E677F.
The following hex pattern can be used to is 41 39 46 0C 74 04 locate the bytes to patch in other versions of the game.
Those bytes need to be replaced with 41 39 46 0C **EB** 04.
This patches the `je` (74) instruction to be `jmp` (EB)


## Additional Notes:
No Magic byte sequence to start the save data unlike Cold Steel 1 and Cold Steel 2 on PC
Mira offset = 0x682A4
Sepith Mass offset = 0x68260
Playtime (double type) offset = 0x7CA58 (PS4 0x7D368?)
First Character location offset = 0x153A8 (stride between characters is 960 bytes)

### Character location/animation Data
The player location offset is critical align to make sure the player character spawns at the correct location after load.
That offset is at 0x153A8 in the PC version. It is made of 3 floats values for the X, Y, Z coordinates.
The stride of the data on PC appears to be 960 bytes and on PS4 976 bytes.
Therefore 16 bytes must be deleted in the PC data for each character model to be aligned to the correct location.
The most important to align is the first as that is the player character. Any issues with NPC models or monsters being in the wrong location can be resolved by switching to different map zone

However for the purpose of just getting the save to load correctly on the PC, adjusting the location data for the first 18 models should suffice.
Plus for each field model location that is fixed decreases the number of bytes that must be deleted in order to align the Gameplay data later on.

### Inventory Data
This is the offset that must be aligned for the save to load the inventory correctly.
Start Inventory Offset = 0x36F1C (PS4 0x37820)
First Item slot is for Team Balm: 2 bytes for the item ID (0x0 is Tear Balm, 0x1 is Teara Balm etc...). The next 2 bytes is the amount of that item in the inventory. The stride of the data appears to be 32 bytes between entries
