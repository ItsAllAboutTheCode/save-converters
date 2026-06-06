# Tales of Graces f Remastered Decyption Notes
Contains notes found during the process to learn how to decrypt a Tales of Graces f Remastered save

## Encryption Algorithm

The Tales of Graces f Remastered save uses AES encryption with a PBKDF2 key

## Remastered Save Data format

The Save data for Tales of Graces has 2 sections.  
Section 1 which is a metadata section that contains the base 64-encoded PNG use for the save file thumbnail and and playtime data.  
Section 2 which contains the actual raw save data (stored as base 64 encoded) and a NobleData section which is base64 encoded as well, but when decrypted it is 1024 bytes.  
The raw save data is the same size as the PS3 data at 79104 bytes.  
The difference the between PS3 save and all other platforms(PC, PS4, PS5, NSW, etc...).  
Is that the PS3 save file integer and float values are stored in big endian format all other platforms are little endian.  
Therefore to convert between PS3 and other platforms, the integer values need to be endian swapped.  

### NOTE
For some reason, the save data writes out both the metadata section and the save data section twice in succession with no changes.
Therefore the save file is always twice the size, than it needs to be
```c#
    private async Task WriteSaveData(int dataNo)
    {
        bool flag = false;
        while (!flag)
        {
            using (SaveLoadStream stream = new SaveLoadStream(FileMode.Open, FileAccess.Write, SaveLoadStream.SaveFileType.eData, dataNo))
            {
                await stream.CheckStart().ConfigureAwait(continueOnCapturedContext: false);
                int length = await Task.Run(delegate
                {
                    mFileParam.pNativeSysParam = new byte[2048];
                    Marshal.Copy(mDeliverySaveData.pParam, length: mDeliverySaveData.mParamLength, destination: mFileParam.pNativeSysParam, startIndex: 0);
                    string s = JsonConvert.SerializeObject(mFileParam);
                    byte[] bytes = Encoding.UTF8.GetBytes(s);
                    AllocSaveLoadBuffer(bytes.Length);
                    Marshal.Copy(bytes, 0, pSaveLoadBuffer[0], bytes.Length);
                    return bytes.Length;
                }).ConfigureAwait(continueOnCapturedContext: false);
                await WriteDataAsync(stream, 0, pSaveLoadBuffer[0], length, 397312).ConfigureAwait(continueOnCapturedContext: false);
                int length2 = await Task.Run(delegate
                {
                    string s = JsonConvert.SerializeObject(mAppDataParam);
                    byte[] bytes = Encoding.UTF8.GetBytes(s);
                    AllocSaveLoadBuffer(bytes.Length);
                    Marshal.Copy(bytes, 0, pSaveLoadBuffer[0], bytes.Length);
                    return bytes.Length;
                }).ConfigureAwait(continueOnCapturedContext: false);
                await WriteDataAsync(stream, 794624, pSaveLoadBuffer[0], length2, 110592).ConfigureAwait(continueOnCapturedContext: false);
                ReleaseSaveLoadBuffer();
            }
            flag = SaveLoadStream.CheckEnd();
        }
    }

    private async Task WriteDataAsync(SaveLoadStream stream, int offset, IntPtr pData, int length, int dataSize = 0)
    {
        byte[] source = new byte[length];
        Marshal.Copy(pData, source, 0, length);
        source = Encryption.Encrypt(source);
        uint crc = CRCHelper.CalculateCRC32(0u, source, 0, source.Length);
        for (int i = 0; i < 2; i++)
        {
            await WriteDataSize(stream, offset, source.Length).ConfigureAwait(continueOnCapturedContext: false);
            await WriteCRC(stream, crc).ConfigureAwait(continueOnCapturedContext: false);
            await stream.WriteAsync(source, 0, source.Length);
            offset += dataSize;
        }
    }
```
