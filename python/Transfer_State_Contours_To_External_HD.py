import os
import shutil
import time
from multiprocessing.dummy import Pool as ThreadPool

STATE_FOLDER = ''
DEST_DRIVE = ''

def log(message):
    global STATE_FOLDER
    
    with open(f"{STATE_FOLDER}\\copy_BUP.log", "a") as f:
        f.write(f"{message}\n")


def copyFolder(sourceFolder):
    folder = sourceFolder.split(':')[-1]
    destFolder = f"{DEST_DRIVE}:{folder}"

    folderName = sourceFolder.split('\\')[-1]
    print(f"COPYING {sourceFolder}\\Shapefiles -> {destFolder}\\Shapefiles")
    shutil.copytree(f"{sourceFolder}\\Shapefiles", f"{destFolder}\\Shapefiles")
    print(f"FINISHED COPYING {sourceFolder}\\Shapefiles -> {destFolder}\\Shapefiles")

    print(f"COPYING {sourceFolder}\\Dwg_Files -> {destFolder}\\Dwg_Files")
    shutil.copytree(f"{sourceFolder}\\Dwg_Files", f"{destFolder}\\Dwg_Files")
    print(f"FINISHED COPYING {sourceFolder}\\Dwg_Files -> {destFolder}\\Dwg_Files")

    if os.path.isfile(f"{sourceFolder}\\{folderName}_Index.geojson"):
        print(f"COPYING {sourceFolder}\\{folderName}_Index.geojson -> {destFolder}\\{folderName}_Index.geojson")
        shutil.copy(f"{sourceFolder}\\{folderName}_Index.geojson", f"{destFolder}\\{folderName}_Index.geojson")
        print(f"FINISHED COPYING {sourceFolder}\\{folderName}_Index.geojson -> {destFolder}\\{folderName}_Index.geojson")

    print(f"COPYING {sourceFolder}\\{folderName}.gdb -> {destFolder}\\{folderName}.gdb")
    shutil.copy(f"{sourceFolder}\\{folderName}.gdb", f"{destFolder}\\{folderName}.gdb")
    print(f"FINISHED COPYING {sourceFolder}\\{folderName}.gdb -> {destFolder}\\{folderName}.gdb")

    log(sourceFolder)


def main():
    global STATE_FOLDER
    global DEST_DRIVE

    STATE_FOLDER = input("Enter the path to the state folder, including drive letter (e.g. W:\\SOUTH_CAROLINA): ")
    DEST_DRIVE = input("Enter the drive letter to copy to (e.g. E): ")

    freeSpace = shutil.disk_usage(DEST_DRIVE).free

    completed = []

    if os.path.exists(f"{STATE_FOLDER}\\copy_BUP.log"):
        with open(f"{STATE_FOLDER}\\copy_BUP.log", "r") as f:
            for line in f.readlines():
                completed.append(line.strip())

    state = STATE_FOLDER.split('\\')[-1]
    countyFolders = [ f.path for f in os.scandir(STATE_FOLDER) if (f.is_dir() and 'County_Contours' in f.path and not 'Empty' in f.path) ]

    copyFolders = []
    copySpace = 0
    
    for folder in countyFolders:
        if folder in completed:
            print(f"Skipping {folder} (already copied)")
            continue
        else:
            folderSize = shutil.disk_usage(folder).used
            if (folderSize + copySpace) < freeSpace:
                copySpace += folderSize
                copyFolders.append(folder)
            else:
                print(f"Will skip {folder} (not enough space)")

    pool = ThreadPool(len(copyFolders))
    pool.map(copyFolder, copyFolders)
    pool.close()
    pool.join()

if __name__ == '__main__':
	main()
