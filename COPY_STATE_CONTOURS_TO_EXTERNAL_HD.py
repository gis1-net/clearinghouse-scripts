import os
import shutil
import time
from multiprocessing.dummy import Pool as ThreadPool

DEST_DRIVE = ''

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

    print(f"COPYING {sourceFolder}\\{folderName}_Index.geojson -> {destFolder}\\{folderName}_Index.geojson")
    shutil.copy(f"{sourceFolder}\\{folderName}_Index.geojson", f"{destFolder}\\{folderName}_Index.geojson")
    print(f"FINISHED COPYING {sourceFolder}\\{folderName}_Index.geojson -> {destFolder}\\{folderName}_Index.geojson")

    

def main():
    global DEST_DRIVE

    sourceStateFolder = input("Enter the path to the state folder, including drive letter (e.g. W:\\SOUTH_CAROLINA): ")
    DEST_DRIVE = input("Enter the drive letter to copy to (e.g. E): ")

    state = sourceStateFolder.split('\\')[-1]

    countyFolders = [ f.path for f in os.scandir(sourceStateFolder) if (f.is_dir() and 'County_Contours' in f.path and not 'Empty' in f.path) ]

    pool = ThreadPool(len(countyFolders))
    pool.map(copyFolder, countyFolders)
    pool.close()
    pool.join()

if __name__ == '__main__':
	main()
