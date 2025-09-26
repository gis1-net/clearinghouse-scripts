import os
import shutil
import time
from multiprocessing.dummy import Pool as ThreadPool

def copyFolder(sourceFolder):
    folder = sourceFolder.split(':')[-1]

    folderName = folder.split('\\')[-1]
    state = folder.split('\\')[-2]
    destFolder = f"data/Contour_Lines/{state.lower()}/{folderName.lower().replace('_county_contours', '')}/GIS1"

    os.system(f"aws s3 cp {sourceFolder}\\{folderName}_Index.geojson s3://storage.data.gis1.net/{destFolder}/index.json --storage-class GLACIER_IR")
    os.system(f"aws s3 sync {sourceFolder}\\Dwg_Files s3://storage.data.gis1.net/{destFolder} --storage-class GLACIER_IR")
    os.system(f"aws s3 sync {sourceFolder}\\Shapefiles s3://storage.data.gis1.net/{destFolder} --storage-class GLACIER_IR")


def main():
    sourceStateFolder = input("Enter the path to the state folder, including drive letter (e.g. W:\\SOUTH_CAROLINA): ")

    state = sourceStateFolder.split('\\')[-1]

    countyFolders = [ f.path for f in os.scandir(sourceStateFolder) if (f.is_dir() and 'County_Contours' in f.path and not 'Empty' in f.path ) ]

    pool = ThreadPool(len(countyFolders))
    pool.map(copyFolder, countyFolders)
    pool.close()
    pool.join()

if __name__ == '__main__':
	main()
