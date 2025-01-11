# [SPT-3.9.8 donwpatcher](https://52sierra-main.github.io/spt-3.9.8downpatcher/)

scripts for creating binary patches for directories.  
currently being used to create downpatches for latest tarkov client to make it compatible with spt 3.9

### patch_generator  
will compare the source and target directories recursively and create a patch directory which mimics the folder structure.  
the path for these directories must be set manually(check the source code).  
it will then create the binary diff files and place them where the target file's location is in the folder structure.  
it also creates another replicate folder structure containing the files that exists in the target but not in the source so that it can be pasted in the patching process.  
check the script for all the files relative location settings.  
the script uses multithreading using threadpoolexecutor.  

  
### patcher  
will apply the patch using the patch folder, delete list, and the additional folder created by the patch generator.  
the .info metadata file must be created manually(just use notepad to create .txt and rename it into filename.info, check the source to see how it should look like).  
the version line in the metadata file is used to check the patchability of the selected directory.  
it should be placed in the root of the patcher folder.
the patcher will prompt the user to choose the directory that needs patching with tkinker.  
once the user chooses the directory, the rest of the process including patching and copy-pasting the additional files is automatic.  
it will auto delete the specified files(delete list).  
this also is multithreaded using threadpoolexecutor.  
you can use pyinstaller to build it into a portable exe file.  
recommended command is->  pyinstaller --onefile --console filename.py
  
  
  
the patcher folder package should look like this  
  
![image](https://github.com/user-attachments/assets/5225de4e-e724-48d3-a2b4-dfee109d7482)

