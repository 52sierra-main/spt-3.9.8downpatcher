#### discord: https://discordapp.com/users/52sierra  
## [github repository](https://github.com/52sierra-main/spt-3.9.8downpatcher)

scripts for creating binary patches for directories.  
currently being used to create downpatches for latest tarkov client to make it compatible with spt 3.9  
### [latest patcher link](https://drive.google.com/drive/folders/1_BsH7_F-xRXZYcMFnu4R5Y9b6tgUJ1ol?usp=sharing)  
This is probably what you're looking for.  
Downgrades the latest tarkov client and installs spt 3.9.8.  
Includes patcher, patchfiles and instructions.

### patch_generator  
will compare the source and target directories recursively and create a patch directory which mimics the folder structure.  
The path for these directories must be set manually(check the source code).  
It will then create the binary diff files and place them where the target file's location is in the folder structure.  
It also creates another replicate folder structure containing the files that exists in the target but not in the source so that it can be pasted in the patching process.  
Another output is the delete list that makes a txt file listing the files that are in the source but not in the target so it can be used by the patcher for removal.  
Check the script for all the files relative location settings.  
The script uses multithreading using threadpoolexecutor.  

  
### patcher  
will apply the patch using the patch folder, delete list, and the additional folder created by the patch generator.  
The .info metadata file must be created manually(just use notepad to create .txt and rename it into filename.info, check the source to see how it should look like).  
The version line in the metadata file is used to check the patchability of the selected directory.  
It should be placed in the root of the patcher folder.
The patcher will prompt the user to choose the directory that needs patching with tkinter.  
Once the user chooses the directory, the rest of the process including patching and copy-pasting the additional files is automatic.  
It will auto delete the specified files(delete list).  
This also is multithreaded using threadpoolexecutor.  
You can use pyinstaller to build it into a portable exe file.  
Recommended command is->  pyinstaller --onefile --console filename.py
  
  
  
the patcher folder package should look like this  
  
![image](https://github.com/user-attachments/assets/5225de4e-e724-48d3-a2b4-dfee109d7482)

