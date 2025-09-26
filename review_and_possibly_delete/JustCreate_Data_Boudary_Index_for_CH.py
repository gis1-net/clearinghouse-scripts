"""
Script Name: Contour Index Processing Script
Created by: Juan Machado - GIS1.net
Date: 2/2/2025

Description:
Processes mosaic dataset boundaries and creates index tiles with data limits.
Generates final GeoJSON index file for county contours.

Dependencies: ArcGIS Pro with default licenses
"""

import arcpy
import os
import datetime
import subprocess
import sys

state_name = None
county_name = None

def clear_screen():
    subprocess.call("cls", shell=True)

def log(message):
    if not state_name or not county_name:
        raise ValueError("State and County names must be defined before logging.")
    log_dir = f"W:\\{state_name}\\{county_name}_County_Contours"
    log_file = os.path.join(log_dir, "ContourIndexProcessing.log")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[{timestamp}] {message}")
    try:
        os.makedirs(log_dir, exist_ok=True)
        with open(log_file, "a") as file:
            file.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Logging failed: {e}")

def main():
    clear_screen()
    start_time = datetime.datetime.now()
    global state_name, county_name

    # Parameter handling
    if len(sys.argv) >= 3:
        state_name = sys.argv[1].strip().replace(" ", "_").upper()
        county_name = sys.argv[2].strip()
    else:
        state_name = input("Enter State Name: ").strip().replace(" ", "_").upper()
        county_name = input("Enter County Name: ").strip()

    log(f"Starting processing for {state_name}, {county_name} County")



      

    # Path configuration
    base_path = f"W:\\{state_name}\\{county_name}_County_Contours"
    index_5000_feature_class = os.path.join(base_path, f"{county_name}_County_Contours.gdb", "Index_5000Ft")
    input_mosaic_dataset = os.path.join(base_path, "Contours_Step1.gdb", "Mosaic_Dataset_UTM")
    
    contour_gdb = os.path.join(base_path, f"{county_name}_County_Contours.gdb")
    step1_gdb = os.path.join(base_path, "Contours_Step1.gdb")
    output_geojson = os.path.join(base_path, f"{county_name}_County_Contours_Index.geojson")
    boundary_utm = os.path.join(contour_gdb, "Mosaic_Boundary_UTM")
    

    try:
        arcpy.env.overwriteOutput = True
        arcpy.CheckOutExtension("3D")
        arcpy.CheckOutExtension("spatial")

        # Process 1: Define Mosaic Dataset NoData
        log("Defining mosaic dataset NoData values")
        md_nodata = arcpy.management.DefineMosaicDatasetNoData(
            input_mosaic_dataset, 
            num_bands=1, 
            bands_for_nodata_value=[["ALL_BANDS", "0"]]
        )[0]

        # Process 2: Build Footprints
        log("Building mosaic dataset footprints")
        md_footprints = arcpy.management.BuildFootprints(
            md_nodata,
            min_data_value=0.5,
            max_data_value=4294967295,
            approx_num_vertices=1000
        )[0]

        # Process 3: Export Mosaic Boundary (FIXED)
        log("Exporting mosaic boundary geometry")
                
        # Add explicit cleanup
        if arcpy.Exists(boundary_utm):
            log(f"Deleting existing {boundary_utm}")
            arcpy.management.Delete(boundary_utm)
            
        arcpy.management.ExportMosaicDatasetGeometry(md_footprints, boundary_utm)


        # Process 4: Project to State Plane
        log("Projecting to SC State Plane")
        boundary_sp = os.path.join(contour_gdb, "Smoothed_PAEK_10FT", "Mosaic_Boundary_SP")
        sr = arcpy.SpatialReference(6557)  # NAD 1983 2011 SC StatePlane (Intl Feet)
        arcpy.management.Project(boundary_utm, boundary_sp, sr)

        # Process 5: Intersect with Index
        log("Intersecting boundaries with index")
        data_limits_step1 = os.path.join(contour_gdb, "Data_Limits_Step1")
        arcpy.analysis.Intersect([[boundary_sp, ""], [index_5000_feature_class, ""]], data_limits_step1)

        # Process 6: Dissolve Features
        log("Dissolving data limits")
        data_limits_sp = os.path.join(contour_gdb, "Data_Limits_SP")
        arcpy.management.Dissolve(data_limits_step1, data_limits_sp)

        # Process 7: Clip Index Features
        log("Clipping index features")
        index_clipped = os.path.join(contour_gdb, "Index_5000Ft_w_Limits")
        arcpy.analysis.Clip(index_5000_feature_class, data_limits_sp, index_clipped)

        # Process 8: Cleanup Fields (Temporary Implementation - Will never use again)
        log("Cleaning up fields")
        fields_to_delete = ["LABEL_X", "LABEL_Y", "NAME_X", "NAME_Y"] + [
            "Abbeville", "Aiken", "Allendale", "Anderson", "Bamberg", "Barnwell",
            "Beaufort", "Berkeley", "Calhoun", "Charleston", "Cherokee", "Chester",
            "Chesterfield", "Clarendon", "Colleton", "Darlington", "Dillon",
            "Dorchester", "Edgefield", "Fairfield", "Florence", "Georgetown",
            "Greenville", "Greenwood", "Hampton", "Horry", "Jasper", "Kershaw",
            "Lancaster", "Laurens", "Lee", "Lexington", "McCormick", "Marion",
            "Marlboro", "Newberry", "Oconee", "Orangeburg", "Pickens", "Richland",
            "Saluda", "Spartanburg", "Sumter", "Union", "Williamsburg", "York",
            "P_D_Area"
        ]
        index_clean = arcpy.management.DeleteField(index_clipped, fields_to_delete)[0]

        # Process 9: Final Projection to WGS84
        log("Projecting to WGS84")
        index_wgs = os.path.join(contour_gdb, "Index_5000Ft_WGS")
        arcpy.management.Project(index_clean, index_wgs, 4326)  # WGS84

        # Process 10: Export to GeoJSON
        log("Generating final GeoJSON")
        arcpy.conversion.FeaturesToJSON(
            index_wgs, 
            output_geojson, 
            geoJSON="GEOJSON"
        )

    except Exception as e:
        log(f"Processing failed: {str(e)}")
        raise
    finally:
        arcpy.CheckInExtension("3D")
        arcpy.CheckInExtension("spatial")
        log(f"Total processing time: {datetime.datetime.now() - start_time}")

if __name__ == "__main__":
    main()