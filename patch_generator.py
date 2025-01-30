import filecmp
import sys
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import subprocess
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import Tk, filedialog
# tqdm is external, must pip install in your python environment

def get_base_dir():
    """Return the base directory of the script or executable."""
    if getattr(sys, 'frozen', False):  # Check if running in a PyInstaller executable
        return os.path.dirname(sys.executable)  # Temporary directory for bundled files
    else:
        return os.path.dirname(os.path.abspath(__file__))  # Script's directory
    
script_dir = get_base_dir()

output_origin = os.path.join(script_dir, "patch_origin_do_not_edit")
output_inherit = os.path.join(script_dir, "patch_output")

def duplicate_directory(origin, inherit):
    """for duplicating origin patch output directory"""
    try:
        if os.path.exists(inherit):
            raise FileExistsError(f"The target directory '{inherit}' already exists.")
        shutil.copytree(origin, inherit)
        print(f"Successfully duplicated '{origin}' to '{inherit}'.")
    except Exception as e:
        print(f"Error duplicating directory: {e}")

duplicate_directory(output_origin, output_inherit)

# Paths
source = None  # latest tarkov client that NEEDS patching, chosen using tkinter
dest = None  # tarkov client 0.14 for spt 3.9, chosen using tkinter
patch_output = os.path.join(script_dir, "patch_output", "patchfiles")  # patch files output folder
missing_dir = os.path.join(script_dir, "patch_output", "additional_files")  # files that exist in dest but not in source will be copied here
hdiffz_path = os.path.join(script_dir, "bin", "x64", "hdiffz.exe")  # Path to hdiffz 
delete_list_file = os.path.join(script_dir, "patch_output", "delete_list.txt")  # for deleting junk in patching process
version = os.path.join(script_dir, "patch_output", "metadata.info")

# create directories(probably not need this)
os.makedirs(patch_output, exist_ok=True)
os.makedirs(missing_dir, exist_ok=True)

# use Tkinker to prompt the choose folder popup
def choose_directory():
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    directory = filedialog.askdirectory(title="choose directory(read console)")
    if not directory:
        input("choose something")
        exit(1)
    return directory

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

 
def version_info(file_path):
    """
    edit version info on a .info file
    """
    try:
        # Prompt user for input
        versioncode = input("enter version(ex: 1.1.1.1): ")
        datecode = input("Enter release date: ")

        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        lines[0] = versioncode + '\n'
        lines[1] = datecode + '\n'

        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

        print(f"Successfully updated version info of {file_path}.")

    except FileNotFoundError:
        print(f"ERROR: The file {file_path} does not exist.")
    except ValueError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



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
        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = [executor.submit(process_file, file) for file in files_to_process]
            for future in as_completed(futures):
                progress.update(1)

# everything starts here
if __name__ == "__main__":
    print("choose the directory that has the targeted version")
    dest = choose_directory()
    print("choose the directory that needs to be patched")
    source = choose_directory()
    print("Starting patch creation...")
    process_directory()
    detect_files_to_delete()
    version_info(version)
    input("Patch creation complete.")
