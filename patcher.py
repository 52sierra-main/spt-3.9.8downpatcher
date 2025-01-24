import os
import sys
import shutil
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tkinter import Tk, filedialog
import time
import win32api # pip install pywin32
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm # pip install tqdm

# in order to compile this and keep all the dialogues, in terminal, do [pyinstaller --console --onefile thisfilename.py]
# --onefile make it into one executable and not a slurge of files of which many people start asking you dumb shit cuz they decided to double click that instead of the exe for whatever reason

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

def patch_check(dest_dir):
    """check for broken files"""
    typeA = ["tgikuvgt0dcv"]
    typeB = ["KpuvcnnaGHV"]
    root = os.path.basename(os.path.normpath(dest_dir))
    print(root)

    Alist = ["".join([chr(ord(c) - 2) for c in name]) for name in typeA]
    Blist = ["".join([chr(ord(c) - 2) for c in name]) for name in typeB]

    for A in Alist: 
        if os.path.exists(os.path.join(dest_dir, A)):
            raise Exception("오류, 코드 3")
        
    if root in Blist:
            raise Exception("오류, 코드 3")

    for B in Blist:
        if os.path.exists(B):
            raise Exception("오류, 코드 3")

# check client version
def version_check(file_path):
    """get escapefromtarkov.exe version"""
    try:
        info = win32api.GetFileVersionInfo(file_path, '\\')
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        return version
    except Exception as e:
        print(f"오류, 타르코프 실행파일 버전 불러오기 실패, {file_path}. Error: {e}")
        return None

# use Tkinker to prompt the choose folder popup
def choose_directory():
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    directory = filedialog.askdirectory(title="복사 붙여넣은 타르코프 폴더를 선택해주세요")
    if not directory:
        input("아무것도 선택하지 않았습니다.")
        exit(1)
    
    # logic for checking for EscapeFromTarkov.exe and it's version as a foolproof design
    executable = os.path.join(directory, "EscapeFromTarkov.exe") 
    if not executable:
        input("선택한 폴더에 타르코프 실행파일이 없습니다. 올바른 폴더를 선택해주세요.")
        exit(1)
    if version_check(executable) != metadata['version']: # compares the version info on the metadata file and the exe file itself so ppl won't screw up
        input("선택한 폴더의 클라이언트 버전이 패쳐와 호환되지 않습니다! 본섭 업데이트 상태와 패쳐의 최신버전 유무를 확인해주세요!")
        exit(1)
    return directory


# read metadata from the .info file
def read_metadata(script_dir):
    
    info_file = next(Path(script_dir).glob("*.info"), None)
    if not info_file:
        raise FileNotFoundError(f"메타데이터 파일 찾기 실패")

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
        input(f"경고!: 타겟 파일을 찾지 못하였습니다! 타르코프 클라이언트를 확인하고 다시 복사해주시기 바랍니다! 파일: {dest_file} ")
        exit(1)

    # apply 
    try:
        subprocess.run(
            [hpatchz_path, "-f", str(dest_file), str(hdiff_file), str(dest_file)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        tqdm.write(f"Patched: {dest_file}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to patch {dest_file}. Error: {e.stderr.decode()}")


def process_patches(dest_dir):
    # Process all .hdiff files in the patch directory.
    hdiff_files = list(Path(patch_dir).rglob("*.hdiff"))
    if not hdiff_files:
        input("패치 폴더 없음.")
        exit(1)

    print(f"Found {len(hdiff_files)} patch files. Applying...")

# used tqdm to create a progress bar
    with tqdm(total=len(hdiff_files), desc="Processing files", unit="hdiff") as progress:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(apply_patch, hdiff, dest_dir) for hdiff in hdiff_files]
            for future in as_completed(futures):
                progress.update(1)

    #with ThreadPoolExecutor(max_workers=6) as executor:
    #    for hdiff in hdiff_files:
    #        executor.submit(apply_patch, hdiff, dest_dir)


def finalize_patch(dest_dir):
    """ delete stuff and add additional files"""
    print("------------------")
    print("파일 추가 및 제거")
    print("------------------")

    # read the list of files to delete from delete_list.txt
    delete_list_file = os.path.join(script_dir, "delete_list.txt")
    files_to_delete = []

    if os.path.exists(delete_list_file):
        with open(delete_list_file, "r", encoding="utf-8") as f:
            files_to_delete = [line.strip() for line in f if line.strip()]
    else:
        input(f"제거 파일 리스트 없음: {delete_list_file}")
        exit(1)

    # remove files 
    for file in files_to_delete:
        file_path = os.path.join(dest_dir, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"제거된 파일: {file_path}")
            except Exception as e:
                print(f"파일 제거 실패: {file_path}. Error: {e}")
        else:
            print(f"파일 찾지 못함(무시하셔도 상관없습니다): {file_path}")

    # remove empty directories
    print("빈 폴더 제거중...")
    for root, dirs, files in os.walk(dest_dir, topdown=False):  # Process subdirectories first
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            if not os.listdir(dir_path):  # Check if the directory is empty
                try:
                    os.rmdir(dir_path)
                    print(f"폴더 제거 완료: {dir_path}")
                except Exception as e:
                    print(f"폴더 제거 실패 {dir_path}. Error: {e}")
            else:
                print(f"폴더 확인 완료: {dir_path}")

    # copy additional files
    additional_files_dir = os.path.join(script_dir, "additional_files")
    if os.path.exists(additional_files_dir):
        shutil.copytree(
            additional_files_dir,
            dest_dir,
            dirs_exist_ok=True  # allows merging directories
        )
        print(f"추가파일 카피 {additional_files_dir} 에서 {dest_dir}")
    else:
        input(f"추가파일 폴더 찾지 못함: {additional_files_dir}")
        exit(1)


if __name__ == "__main__":
    try:
        print("메타데이터 읽는 중...")
        time.sleep(1)
        metadata = read_metadata(script_dir)
        print(f"Version: {metadata['version']}")
        print(f"Title: {metadata['title']}")
        print(f"Description: {metadata['description']}")
        print("엔터를 눌러 진행하세요")
        os.system("pause")

        # tkinter prompt
        print("패치할 타르코프 폴더를 선택하세요:")
        dest_dir = choose_directory()
        patch_check(dest_dir)

        print("패치 적용중...")
        process_patches(dest_dir)
        print("패치적용완료")
        print("마무리 중...")
        finalize_patch(dest_dir)
        print("모든 작업 완료, 즐거운 게임 되세요")
        input("엔터를 눌러 종료하세요...")
    except Exception as e:
        print(f"ERROR: {e}")
