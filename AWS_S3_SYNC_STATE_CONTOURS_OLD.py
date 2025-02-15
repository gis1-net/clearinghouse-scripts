import os

def main():
    sourceStateFolder = input("Enter the path to the state folder, including drive letter (e.g. W:\SOUTH_CAROLINA): ")


    state = folder.split('\\')[-1]

    countyFolders = [ f.path for f in os.scandir(sourceStateFolder) if f.is_dir() ]

    for sourceCountyFolder in countyFolders:
        if not 'Empty' in sourceCountyFolder and sourceCountyFolder.endswith('_County_Contours'):
            folderName = sourceCountyFolder.split('\\')[-1]
            destCountyFolder = f"data/Contour_Lines/{state.lower()}/{folderName.lower().replace('_county_contours', '')}/GIS1"

            os.system(f"aws s3 cp {sourceCountyFolder}\\{folderName}_Index.geojson s3://storage.data.gis1.net/{destCountyFolder}/index.json")
            os.system(f"aws s3 sync {sourceCountyFolder}\\Dwg_Files s3://storage.data.gis1.net/{destCountyFolder}")
            os.system(f"aws s3 sync {sourceCountyFolder}\\Shapefiles s3://storage.data.gis1.net/{destCountyFolder}")

if __name__ == '__main__':
	main()
