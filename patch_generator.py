import filecmp
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import subprocess

# Paths
source = r'C:\patch_maker\Escape from Tarkov'  # latest tarkov client THAT NEEDS PATCHING
dest = r'C:\patch_maker\target'  # tarkov client 0.14 for spt 3.9
patch_output = r'C:\patch_maker\patch'  # patch files output folder
missing_dir = r'C:\patch_maker\additional_files'  # files that exist in dest but not in source will be copied here
hdiffz_path = r'C:\patch_maker\bin\x64\hdiffz.exe'  # Path to hdiffz 

# create directories(probably not need this)
os.makedirs(patch_output, exist_ok=True)
os.makedirs(missing_dir, exist_ok=True)

#  process a single file to create a patch
def process_file(dest_file):
    
    # derive source file path
    rel_path = os.path.relpath(dest_file, dest)
    source_file = os.path.join(source, rel_path)
    patch_file = os.path.join(patch_output, rel_path + ".hdiff")

    # ensure patch directory
    os.makedirs(os.path.dirname(patch_file), exist_ok=True)

    # check if source file exist
    if not os.path.exists(source_file):
        print(f"WARNING: Missing source file for {dest_file}. Copying to missing files directory.")
        missing_file_path = os.path.join(missing_dir, rel_path)
        os.makedirs(os.path.dirname(missing_file_path), exist_ok=True)
        shutil.copy(dest_file, missing_file_path)
        return

    # check if files are identical
    if filecmp.cmp(source_file, dest_file, shallow=False):
        print(f"Skipping identical file: {dest_file}")
        return

    # create patch
    try:
        subprocess.run(
            [hdiffz_path, "-m-1", "-cache", "-SD", "-c-bzip2", source_file, dest_file, patch_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Processed {dest_file} successfully.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to process {dest_file}. Error: {e}")

# traverse the destination directory and create patch in parallel
def process_directory():
    
    files_to_process = []
    for root, _, files in os.walk(dest):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    # threadPoolExecutor for parallel
    with ThreadPoolExecutor() as executor:
        executor.map(process_file, files_to_process)

# everything starts here
if __name__ == "__main__":
    print("Starting patch creation...")
    process_directory()
    print("Patch creation complete.")
