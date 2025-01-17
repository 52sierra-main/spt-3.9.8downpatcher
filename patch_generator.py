import filecmp
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import subprocess
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
# tqdm is external, must pip install in your python environment

# Paths
source = r'C:\patch workspace\patch_maker\Escape from Tarkov'  # latest tarkov client THAT NEEDS PATCHING
dest = r'C:\patch workspace\patch_maker\target'  # tarkov client 0.14 for spt 3.9
patch_output = r'C:\patch workspace\patch_maker\patchfiles'  # patch files output folder
missing_dir = r'C:\patch workspace\patch_maker\additional_files'  # files that exist in dest but not in source will be copied here
hdiffz_path = r'C:\patch workspace\patch_maker\bin\x64\hdiffz.exe'  # Path to hdiffz 
delete_list_file = r'C:\patch workspace\patch_maker\delete_list.txt' # for deleting junk in patching process

# create directories(probably not need this)
os.makedirs(patch_output, exist_ok=True)
os.makedirs(missing_dir, exist_ok=True)

def additional_files(rel_path, dest_file):
    missing_file_path = os.path.join(missing_dir, rel_path)
    os.makedirs(os.path.dirname(missing_file_path), exist_ok=True)
    shutil.copy(dest_file, missing_file_path)

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
        tqdm.write(f"WARNING: Missing source file for {dest_file}. Copying to missing files directory.")
        additional_files(rel_path, dest_file)
        return

    # check if files are identical
    if filecmp.cmp(source_file, dest_file, shallow=False):
        tqdm.write(f"Skipping identical file: {dest_file}")
        return

    # create patch
    try:
        subprocess.run(
            [hdiffz_path, "-m-1", "-cache", "-SD", "-c-bzip2", source_file, dest_file, patch_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        tqdm.write(f"Processed {dest_file} successfully.")
    # when error, just save the thing for copy paste
    except subprocess.CalledProcessError as e:
        additional_files(rel_path, dest_file)
        print(f"ERROR: Failed to process {dest_file}. Error: {e}")

def detect_files_to_delete():
    """detect files in source that are not in target and save their paths."""
    print("Detecting...")

    files_to_delete = []
    for root, _, files in os.walk(source):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), source)
            dest_file = os.path.join(dest, rel_path)
            if not os.path.exists(dest_file):
                files_to_delete.append(rel_path)

    # save the list 
    with open(delete_list_file, 'w', encoding='utf-8') as f:
        for file in files_to_delete:
            f.write(file + '\n')

    print(f"Detected {len(files_to_delete)} files to delete. Saved to {delete_list_file}.")



# traverse the destination directory and create patch in parallel
def process_directory():
    
    files_to_process = []
    for root, _, files in os.walk(dest):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    # threadPoolExecutor for parallel(below was the original code)
    #with ThreadPoolExecutor(max_workers=14) as executor:
    #    executor.map(process_file, files_to_process)

    # used tqdm to create a progress bar
    with tqdm(total=len(files_to_process), desc="Processing files", unit="file") as progress:
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(process_file, file) for file in files_to_process]
            for future in as_completed(futures):
                progress.update(1)

# everything starts here
if __name__ == "__main__":
    print("Starting patch creation...")
    process_directory()
    detect_files_to_delete()
    input("Patch creation complete.")
