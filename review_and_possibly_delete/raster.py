# -*- coding: utf-8 -*-
import arcpy
import os
 
# Allow overwriting outputs
arcpy.env.overwriteOutput = False
 
# Path to the state directory containing multiple county folders
state_folder = r"Z:\VIRGINIATEST2"
 
# Path for raster proxy cache
pixel_cache_location = r"C:\Users\Chad\AppData\Local\ESRI\rasterproxies\Mosaic_Dataset_UTM"
 
# Loop through each folder that ends with "_Contours"
for folder_name in os.listdir(state_folder):
    if folder_name.endswith("_Contours"):
        county_folder = os.path.join(state_folder, folder_name)
        # Define paths
        tif_files_utm = os.path.join(county_folder, "Tif_Files_UTM")
        mosaic_dataset = os.path.join(county_folder, "Contours_Step1.gdb", "Mosaic_Dataset_UTM")
 
        print(f"Processing: {folder_name}")
        print(f"  TIF folder: {tif_files_utm}")
        print(f"  Mosaic dataset: {mosaic_dataset}")
 
        # Only run if both the raster folder and mosaic dataset exist
        if arcpy.Exists(mosaic_dataset) and os.path.isdir(tif_files_utm):
            try:
                arcpy.management.AddRastersToMosaicDataset(
                    in_mosaic_dataset=mosaic_dataset,
                    raster_type="Raster Dataset",
                    input_path=[tif_files_utm],
                    update_cellsize_ranges="UPDATE_CELL_SIZES",
                    update_boundary="UPDATE_BOUNDARY",
                    update_overviews="NO_OVERVIEWS",
                    maximum_cell_size=0,
                    minimum_dimension=1500,
                    spatial_reference="",
                    filter="",
                    sub_folder="NO_SUBFOLDERS",
                    duplicate_items_action="EXCLUDE_DUPLICATES",
                    build_pyramids="NO_PYRAMIDS",
                    calculate_statistics="CALCULATE_STATISTICS",
                    build_thumbnails="NO_THUMBNAILS",
                    operation_description="",
                    force_spatial_reference="NO_FORCE_SPATIAL_REFERENCE",
                    estimate_statistics="ESTIMATE_STATISTICS",
                    cache_location=pixel_cache_location
                )
                print(f" Successfully added rasters to: {mosaic_dataset}")
            except Exception as e:
                print(f"  Failed to add rasters to: {mosaic_dataset}")
                print(f"  Error: {e}")
        else:
            print(f"  Skipped: Missing raster folder or mosaic dataset.")