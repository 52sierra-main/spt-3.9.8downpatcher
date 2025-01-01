import filecmp
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import subprocess

# Paths and settings
source = r'C:\patch_maker\Escape from Tarkov'  # Replace with the actual source path
dest = r'C:\patch_maker\target'  # Replace with the actual destination path
patch_output = r'C:\patch_maker\patch'  # Replace with the actual patch output path
missing_dir = r'C:\patch_maker\additional_files'  # Replace with the actual missing files directory
hdiffz_path = r'C:\patch_maker\bin\x64\hdiffz.exe'  # Path to the hdiffz executable

# Ensure necessary directories exist
os.makedirs(patch_output, exist_ok=True)
os.makedirs(missing_dir, exist_ok=True)

def process_file(dest_file):
    """Process a single file to create a patch."""
    # Derive source file path
    rel_path = os.path.relpath(dest_file, dest)
    source_file = os.path.join(source, rel_path)
    patch_file = os.path.join(patch_output, rel_path + ".hdiff")

    # Ensure the patch directory exists
    os.makedirs(os.path.dirname(patch_file), exist_ok=True)

    # Check if source file exists
    if not os.path.exists(source_file):
        print(f"WARNING: Missing source file for {dest_file}. Copying to missing files directory.")
        missing_file_path = os.path.join(missing_dir, rel_path)
        os.makedirs(os.path.dirname(missing_file_path), exist_ok=True)
        shutil.copy(dest_file, missing_file_path)
        return

    # Check if files are identical
    if filecmp.cmp(source_file, dest_file, shallow=False):
        print(f"Skipping identical file: {dest_file}")
        return

    # Create the patch
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

def process_directory():
    """Traverse the destination directory and process all files in parallel."""
    files_to_process = []
    for root, _, files in os.walk(dest):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        executor.map(process_file, files_to_process)

if __name__ == "__main__":
    print("Starting patch creation...")
    process_directory()
    print("Patch creation complete.")
