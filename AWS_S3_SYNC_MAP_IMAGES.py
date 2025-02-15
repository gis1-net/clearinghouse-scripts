import os
import shutil
import time
from multiprocessing.dummy import Pool as ThreadPool

def copyFolder(sourceFolder):
    folderName = sourceFolder.split('/')[-1]
    destFolder = f"assets/map_images/counties/{folderName}"
    
    print(f"COPYING {sourceFolder} -> {destFolder}")
    os.system(f"aws s3 sync {sourceFolder} s3://storage.data.gis1.net/{destFolder}")
    print(f"FINISHED COPYING {sourceFolder} -> {destFolder}")

def main():
    sourceFolder = '/home/nick/Documents/Map_Images/counties'

    stateFolders = [ f.path for f in os.scandir(sourceFolder) if f.is_dir() ]

    pool = ThreadPool(len(stateFolders))
    pool.map(copyFolder, stateFolders)
    pool.close()
    pool.join()

if __name__ == '__main__':
	main()
