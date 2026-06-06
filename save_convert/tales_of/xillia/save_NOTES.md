# Tales of Xillia Remastered PS3 -> Remastered Save Convert Notes
Contains notes found during the process of learning how to convert a PS3 save to the Remastered platform


## Save Types for PS3 and Remastered game platforms

The save types for the game determines whether the save shows up
as either a Quick Save, Autosave or Normal Save such as 001, 002, etc...  
The PS3 game has two save types:  
1 - For Normal Save  
2 - For Quick Save  

There are 3 save types for the Remastered game:  
0 - For Normal Save  
1 - For Auto Save  
2 - For Quick Save  

## Differences between the PS3 Save and Remastered save

### PS3 Save
The PS3 Save is a binary save file of fixed size 453760.  

The first 16 bytes of the Save file contain a header that encodes the save version, the number of save blocks which is always 0x22(34).  
Next the total save file which is always 0x6ec80(453760).  
Finally it contains the save type which is either 1 or 2. 

See [tales_of_xillia_structs.py](./tales_of_xillia_structs.py) for more information.  

### Remastered platform Save 
The Remastered platform save format is a encrypted JSON
which contains a header keys such as the save data type, save data version, the screenshot of the screen taking during save stored as a array of ints in the `mScreenCaputure` key, as well as othe keys that  determine if how the save is displayed.

* `mSaveListParam` - Determines the number that will be placed next to the save in the load menu
* `mMapID` - ID of the Map that will be shown when loading the game
* `mLevel` - The Level of Jude when on his route or Millia when on her route
* `mPlayTime` - Playtime for the game stored as 1/60th of a second. To convert to hours divide by 60^3, to minutes divied by 60 and to seconds divide by 60
* `mRoutePartyID` - Determines if the game is on Jude (1) or Milla(2) route. The save will be Blue for Jude and Pink for Milla
* `mIsGameClearMark` - Adds a star to the save if either the [PARTY_PROFILE_DATA](./dicts/tales_of_xillia_party_profile_dict.py) save block`mGameClearCountJUR` (Jude) or `mGameClearCountMIR` (Milla) key is above 0
* `mSscenarioFlag` - The flag indicates the Main Game scenario that should apear when loading the save
* `mDLCUsedData` - Used DLC with the save. This value is sourced from the [SAVE_DATA_ID_ITEM_DATA_MANAGER](./dicts/tales_of_xillia_item_manager_dict.py) save block from the `mDownloadContentsUseFlag` key.  
  NOTE: The save converter does not set this value in case the user doesn't have the DLC for the Remastered Save version
* `mDLCHaveData` - Available DLC items avilable for redemption with the for the game. Stored in the [SAVE_DATA_ID_ITEM_DATA_MANAGER](./dicts/tales_of_xillia_item_manager_dict.py#L156) `mDLCCheckItemID` key


See [tales_of_xillia_dicts.py](./tales_of_xillia_dicts.py) for more information.  

### PC-Only: Remastered Platform Bundle Data

The list of Save entries available for load on PC is determined by the contents in the encrypted `Bundle.data` file that is in the same directory as the save.  
Luckily the encryption used is the same as the regular save and this save converter can decrypt/re-encrypt the contents.  
It would look like the following
```JSON
{
  "mVersion": 100,
  "mSaveVSYNC": 0,
  "mSaveLOD": 0,
  "mSaveTextureFiltering": 1,
  "mSaveShadowQuality": 1,
  "mSaveAntialiasing": 1,
  "mSaveFramerate": 120,
  "mSaveEULA": true,
  "mSavePP": true,
  "PickUpSaveDataFileNames": [
    "SaveData0.data",
    "SaveData1.data",
    "SaveData2.data",
    "SaveData3.data",
    "SaveData4.data",
    "SaveData5.data",
    "SaveData6.data",
    "SaveData7.data",
    "",
    "",
    "",
    "",
    ...
  ]
}
```

When addding a new save to load to the game as opposed to overriding an existing save, the `PickUpSaveDataFileNames` array field within the decrypted Bundle.data needs to be modified

## Conversion Notes

The following are list of necessary changes needed to convert a PS3 save to a Remastered game platform. The reverse operation is used to go from a Reamaastered game platform back to PC

### PartyProfile: The `mGradeShopFlag` is 16-bit integer array with length 32 on PS3 and length 64 on PC platforms
### Also the  `mOnOffGradeShopFlag` field does not exist on the PS3 save

When converting back from a Remastered game save, the save converter takes the first 32 entries of the `mGradeShopFlag` array and copies over to the binary save.  
For `mOnOffGradeShopFlag` array, the save converter just copies over the `mGradeShopFlag` array which is the list of grade shop options.  

That occurs in [PartyProfile](./structs/tales_of_xillia_party_profile_struct.py) struct python script.  

### ChangeMap: The `location` field appears to be empty string in the PS3 save

The `location` field should available for the PS3 save at offset 0x4250, but the bytes there appear to be 0.
Looking at the value of the `location` field for the Remastered game save, it is always set to the ChangeMap `map` field.  
The conversion occurs in [ChangeMap](./structs/tales_of_xillia_change_map_struct.py) struct python script.  

### Scenario: Coordinate System for the Player Position and Direction

On PS3, the coordinate system used for Vectors is a coordinate system with negative Z forwards, positive X left, positive Y upwards.  
Furthermore the character direction is stored in radians

On Remastered platforms, the coordinate system used is the Unity left Handed coordincate system  with positive Z forwards, positive X right, positive Y upwards.  
Furthermore the character direction is stored in degrees

Specifically the following keys need to be modified
The `pos` and `start` vectors
The `dir` and `raw` floats.


The [Scenario](./structs/tales_of_xillia_scenario_struct.py) struct python script contains the algorithm for converting the position vector and direction angle between PS3 and remastered platform save formats.

### TreasureBox: The `openRandomData` field does not existi on the PS3 save

The TreasureBox PS3 data doesn't have a `openRandomData` array in the PS3 save, therefore the converted Remastered save will fill the value with '00' bytes.  
The algorithm is for the conversion is in[TreasureBox](./structs/tales_of_xillia_treasure_box_struct.py) struct python script.  

### PlayerStatus: The `mGrowthTransferReferenceData` does not exist on the PS3 save

The PS3 save PlayerStatus data doesn't have the `mGrowthTransferReferenceData` field.
As this field is the same as the `mGrowthTransferData` which the PS3 save does have, the save converter copies it over.  

### PlayerStatus: The `mFormationIndex` field is an integer on PS3 and float on Remastered game platforms

The save converter converts the values to float when creating the save JSON for the Remastered game save.  
When the save is converted back, it gets converted to an int via the `_field_from_dict` method inside of [MarshalStructure](../../structs/marshal_structure.py) class.  

### Configuration: The Remastered Save has additional settings for PC and Consoles.

The configuration data JSON is default constructed with default values of those Settings based on starting a new game from scratch.  
Those default settings are in the [ConfigurationData](./dicts/tales_of_xillia_configuration_data_dict.py) dictionary python script.  
