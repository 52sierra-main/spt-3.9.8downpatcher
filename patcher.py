import os
import sys
import shutil
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tkinter import Tk, filedialog


def get_base_dir():
    """Return the base directory of the script or executable."""
    if getattr(sys, 'frozen', False):  # Check if running in a PyInstaller executable
        return os.path.dirname(sys.executable)  # Temporary directory for bundled files
    else:
        return os.path.dirname(os.path.abspath(__file__))  # Script's directory


# script_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = get_base_dir()

# Paths
patch_dir = os.path.join(script_dir, "patchfiles")
hpatchz_path = os.path.join(script_dir, "bin", "x64", "hpatchz.exe")

log_file = "unipatch-log.txt"


def choose_directory():
    """Prompt the user to choose a directory."""
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    directory = filedialog.askdirectory(title="Select the Directory to Patch")
    if not directory:
        print("No directory selected. Exiting.")
        exit(1)
    return directory


def read_metadata(patch_dir):
    """Read metadata from the .info file."""
    info_file = next(Path(patch_dir).glob("*.info"), None)
    if not info_file:
        raise FileNotFoundError(f"No .info file found in {patch_dir}")

    metadata = {}
    with open(info_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        metadata["version"] = lines[0].strip()
        metadata["title"] = lines[1].strip()
        metadata["description"] = lines[2].strip()
        metadata["dependencies"] = lines[3].strip() if len(lines) > 3 else None

    return metadata


def apply_patch(hdiff_file, dest_dir):
    """Apply a single patch using hpatchz."""
    relative_path = hdiff_file.relative_to(patch_dir).with_suffix("")  # Remove .hdiff suffix

    # Construct the full destination path
    dest_file = Path(dest_dir) / relative_path

    # Check if the destination file exists
    if not dest_file.exists():
        print(f"WARNING: Destination file {dest_file} not found. Skipping patch.")
        return

    # Apply the patch
    try:
        subprocess.run(
            [hpatchz_path, "-f", str(dest_file), str(hdiff_file), str(dest_file)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Patched: {dest_file}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to patch {dest_file}. Error: {e.stderr.decode()}")


def process_patches(dest_dir):
    """Process all .hdiff files in the patch directory."""
    hdiff_files = list(Path(patch_dir).rglob("*.hdiff"))
    if not hdiff_files:
        print("No .hdiff files found in the patch directory.")
        return

    print(f"Found {len(hdiff_files)} patch files. Applying patches...")

    with ThreadPoolExecutor() as executor:
        for hdiff in hdiff_files:
            executor.submit(apply_patch, hdiff, dest_dir)


def finalize_patch(dest_dir):
    """Delete unnecessary files and copy additional files."""
    print("------------------")
    print("파일 추가 및 제거")
    print("------------------")

    # Files to delete
    files_to_delete = [
        "EscapeFromTarkov_BE.exe",
        "Uninstall.exe",
        "UnityCrashHandler64.exe",
        "ConsistencyInfo",
    ]

    # Directories to delete
    dirs_to_delete = [
        "BattlEye",
    ]

    # Remove files
    for file in files_to_delete:
        file_path = os.path.join(dest_dir, file)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found: {file_path}")

    # Remove directories
    for directory in dirs_to_delete:
        dir_path = os.path.join(dest_dir, directory)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Deleted directory: {dir_path}")
        else:
            print(f"Directory not found: {dir_path}")

    # Copy additional files
    additional_files_dir = os.path.join(script_dir, "additional_files", "Escape From Tarkov")
    if os.path.exists(additional_files_dir):
        shutil.copytree(
            additional_files_dir,
            dest_dir,
            dirs_exist_ok=True  # Allows merging directories
        )
        print(f"Copied additional files from {additional_files_dir} to {dest_dir}")
    else:
        print(f"Additional files directory not found: {additional_files_dir}")


if __name__ == "__main__":
    try:
        print("Reading metadata...")
        metadata = read_metadata(patch_dir)
        print(f"Version: {metadata['version']}")
        print(f"Title: {metadata['title']}")
        print(f"Description: {metadata['description']}")

        # 사용자 프롬프트(tkinker)
        print("Please select the directory to patch:")
        dest_dir = choose_directory()

        print("Applying patches...")
        process_patches(dest_dir)
        print("패치적용")
        print("마무리 중...")
        finalize_patch(dest_dir)
        print("모든 작업 완료, 즐거운 게임 되세요")
        input("엔터를 눌러 종료하세요...")
    except Exception as e:
        print(f"ERROR: {e}")
