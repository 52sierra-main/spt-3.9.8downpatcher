import os
import sys
import shutil
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tkinter import Tk, filedialog
import time
# in order to compile this and keep all the dialogues, in terminal, do [pyinstaller --console thisfilename.py](of course get rid of the brackets) 
# you also might want to add --onefile next to the --console argument in order to make it into one executable and not a slurge of files of which many people start asking you dumb shit cuz they decided to double click that instead of the exe for whatever reason

# had to add this because fucking pyinstaller messes up the working directory. without this, it starts at user\blahblah\appdata\blahblah....
def get_base_dir():
    """Return the base directory of the script or executable."""
    if getattr(sys, 'frozen', False):  # Check if running in a PyInstaller executable
        return os.path.dirname(sys.executable)  # Temporary directory for bundled files
    else:
        return os.path.dirname(os.path.abspath(__file__))  # Script's directory


# script_dir = os.path.dirname(os.path.abspath(__file__)) <-this was the original code when i was running off the python file itself
script_dir = get_base_dir()


# Paths
patch_dir = os.path.join(script_dir, "patchfiles")
hpatchz_path = os.path.join(script_dir, "bin", "x64", "hpatchz.exe")
log_file = "unipatch-log.txt"


# use Tkinker to prompt the choose folder popup
def choose_directory():
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    directory = filedialog.askdirectory(title="Select the Directory to Patch")
    if not directory:
        print("No directory selected. Exiting.")
        exit(1)
    return directory


# read metadata from the .info file
def read_metadata(patch_dir):
    
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


# apply a single patch using hpatchz
def apply_patch(hdiff_file, dest_dir):
    relative_path = hdiff_file.relative_to(patch_dir).with_suffix("")  # Remove .hdiff suffix

    # construct the full destination path
    dest_file = Path(dest_dir) / relative_path

    # check for destination file 
    if not dest_file.exists():
        print(f"WARNING: Destination file {dest_file} not found. Skipping patch.")
        return

    # apply 
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
    # Process all .hdiff files in the patch directory.
    hdiff_files = list(Path(patch_dir).rglob("*.hdiff"))
    if not hdiff_files:
        print("No .hdiff files found in the patch directory.")
        return

    print(f"Found {len(hdiff_files)} patch files. Applying patches...")

    with ThreadPoolExecutor(max_workers=6) as executor:
        for hdiff in hdiff_files:
            executor.submit(apply_patch, hdiff, dest_dir)


def finalize_patch(dest_dir):
    # delete stuff and add additional files
    print("------------------")
    print("파일 추가 및 제거")
    print("------------------")

    # files to delete, i don't think this is necessary but i took reference from the output of the existing patch
    files_to_delete = [
        "EscapeFromTarkov_BE.exe",
        "Uninstall.exe",
        "UnityCrashHandler64.exe",
        "ConsistencyInfo",
    ]

    # directories to delete, same for this but i sure don't want bAtTLe EYe to eYE me in the ass while playing spt (jk)
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

    # copy additional files
    additional_files_dir = os.path.join(script_dir, "additional_files", "Escape From Tarkov")
    if os.path.exists(additional_files_dir):
        shutil.copytree(
            additional_files_dir,
            dest_dir,
            dirs_exist_ok=True  # allows merging directories
        )
        print(f"Copied additional files from {additional_files_dir} to {dest_dir}")
    else:
        print(f"Additional files directory not found: {additional_files_dir}")


if __name__ == "__main__":
    try:
        print("메타데이터 읽는 중...")
        time.sleep(1)
        metadata = read_metadata(patch_dir)
        print(f"Version: {metadata['version']}")
        print(f"Title: {metadata['title']}")
        print(f"Description: {metadata['description']}")
        print("엔터를 눌러 진행하세요")
        os.system("pause")

        # tkinter prompt
        print("패치할 타르코프 폴더를 선택하세요:")
        dest_dir = choose_directory()

        print("패치 적용중...")
        process_patches(dest_dir)
        print("패치적용완료")
        print("마무리 중...")
        finalize_patch(dest_dir)
        print("모든 작업 완료, 즐거운 게임 되세요")
        input("엔터를 눌러 종료하세요...")
    except Exception as e:
        print(f"ERROR: {e}")
