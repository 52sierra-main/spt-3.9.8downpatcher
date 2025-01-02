## SPT-3.9.8 donwpatcher 
scripts for creating patches for folders.  
currently being used to create downpatches for latest tarkov client to make it compatible with spt 3.9

[patch generator] will compare the source and target directories recursively and create a patch directory which mimics the folder structure.  
it will then create the binary diff files and place them where the target file's location in the folder structure.  
it also creates another replicate folder structure containing the files that exists in the target but not in the source so that it can be pasted in the patching process.  
check the script for all the files relative location settings.  
!!hdiffz is required in the specified path.!!  
the script uses multithreading wo it will hoard resources for some period of time.  

[patcher] will apply the patch using the patch folder and the additional folder created by the patch generator.  
!!CHECK THE PATH SETTINGS, hpatchz is required in the specified path.!!  
the .info metadata file must be created manually(just use notepad and rename it.  
it will prompt the user to choose the directory that needs patching with tkinker.  
once the user chooses the directory, the rest of the process including patching and copy-pasting the additional files is automatic.  
it will auto delete the specified files(in the source).
this also is multithreaded so it will hoard resources for tens of seconds(20 to 30seconds).  
you can use pyinstaller to build it into a portable exe file.  
recommended command is->  pyinstaller --onefile --console filename.py
