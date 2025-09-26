"""
Script Name: Contour Processing and Smoothing Script
Created by: Juan Machado - GIS1.net
Date: 1/23/2025

Notes: Make sure you run it from the location of ESRI ArcPy needed:
                  cd "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\"
                  .\python.exe D:\scripts\JustExportShapeFiles.py
                  
Description:
This script automates the processing of contour lines using ArcGIS. It performs the following tasks:
    
   Export to shapefiles
   Iterate through all line feature classes in the specified dataset


Outputs:
- Various feature classes and layers representing processed and smoothed contour lines.

Dependencies:
- Requires ArcGIS Pro and licenses for 3D Analyst and Spatial Analyst extensions.

Usage:
- Ensure the input paths and parameters are correctly defined before running the script.
- Execute the script in an environment with ArcGIS Pro installed and the necessary licenses checked out.

1. Using Command-Line Arguments:
    python script.py [STATE] [COUNTY]

    Example:
    python script.py SOUTH_CAROLINA Abbeville

2. Without Command-Line Arguments:
    Run the script directly. It will prompt for the state and county names:
    - Enter the state name (e.g., "South Carolina").
    - Enter the county name (e.g., "Abbeville").

Notes:
- This script overwrites existing output files if they already exist.
- Modify the coordinate system or other parameters as needed for specific datasets.
"""



import arcpy
import os
import datetime
import subprocess

# Define global variables
state_name = None
county_name = None


def clear_screen():
    """Clears the terminal screen."""
    subprocess.call("cls", shell=True)
       
        
# Function to log messages
def log(message):
    """Logs a message with a timestamp."""
    
    if not state_name or not county_name:
        raise ValueError("State and County names must be defined before logging.")
    
    log_dir = f"W:\\{state_name}\\{county_name}_County_Contours"

    log_file = os.path.join(log_dir, "JustExportShapeFiles.log")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"

    # Print to console
    print(formatted_message)

    # Write to log file
    try:
        os.makedirs(log_dir, exist_ok=True)  # Ensure directory exists
        with open(log_file, "a") as file:  # Append mode
            file.write(formatted_message + "\n")
            file.flush()
    except Exception as e:
        print(f"Failed to write log to {log_file}: {e}")


# Added FeatureClassGenerator function

def FeatureClassGenerator(workspace, wild_card, feature_type, recursive):
    with arcpy.EnvManager(workspace=workspace):
        dataset_list = [""]
        if recursive:
            datasets = arcpy.ListDatasets()
            dataset_list.extend(datasets)
 
        for dataset in dataset_list:
            featureclasses = arcpy.ListFeatureClasses(wild_card, feature_type, dataset)
            for fc in featureclasses:
                yield os.path.join(workspace, dataset, fc), fc

# End Added FeatureClassGenerator function



# Main function
def main():
    clear_screen()
    start_time = datetime.datetime.now() 
    global state_name, county_name  # Declare global variables to update them
    
    # Parse state and county from command-line arguments or prompt the user
    if len(sys.argv) >= 3:
        state_name = sys.argv[1].strip()
        county_name = sys.argv[2].strip()
        skip_confirmation = True  # Skip confirmation if parameters are passed
    else:
        state_name = input("Enter the State Name: ").strip()
        county_name = input("Enter the County Name: ").strip()
        skip_confirmation = False  # Require confirmation if no parameters are passed

    # Now that state and county are defined, log the initial message
    log(f"Welcome to the Contour Processing Script.")
    log(f"Processing State: {state_name}, County: {county_name}")


    # Define input and output paths dynamically
    base_path = f"W:\\{state_name}\\{county_name}_County_Contours"
    input_mosaic_dataset = os.path.join(base_path, "Contours_Step1.gdb", "Mosaic_Dataset_UTM")
    output_feature_dataset = os.path.join(base_path, f"{county_name}_County_Contours.gdb", "Smoothed_PAEK_10FT")
    index_5000_feature_class = os.path.join(base_path, f"{county_name}_County_Contours.gdb", "Index_5000Ft")
    contour_lines_sp_feature_class = os.path.join(base_path, "Contours_Step2.gdb", "Contours_SP", "Contour_Lines_SP")
    smoothed_contour_lines_feature_class = os.path.join(base_path, "Contours_Step3.gdb", "Smoothed_Contours", "Smoothed_Contour_Lines")
    shapefile_output_folder = os.path.join(base_path, "Shapefiles")

    # Ensure the output shapefile folder exists
    if not os.path.exists(shapefile_output_folder):
        os.makedirs(shapefile_output_folder)

    # Log initial variables
    log("Initial variables:")
    log(f"input_mosaic_dataset: {input_mosaic_dataset}")
    log(f"output_feature_dataset: {output_feature_dataset}")
    log(f"index_5000_feature_class: {index_5000_feature_class}")
    log(f"contour_lines_sp_feature_class: {contour_lines_sp_feature_class}")
    log(f"smoothed_contour_lines_feature_class: {smoothed_contour_lines_feature_class}")

    # Confirm to proceed if not skipping confirmation
    if not skip_confirmation:
        proceed = input("Do you want to proceed with the script? (y/n): ").strip().lower()
        if proceed != 'y':
            log("Script execution cancelled by user.")
            return

    try:
        # Set environment settings
        arcpy.env.overwriteOutput = True
        log("Environment overwriteOutput set to True.")

        # Check out necessary licenses
        arcpy.CheckOutExtension("3D")
        arcpy.CheckOutExtension("spatial")
        log("Checked out 3D and Spatial Analyst extensions.")

        # Export to shapefiles
        # Iterate through all line feature classes in the specified dataset
        log("Iterating through all line feature classes in the specified dataset.")
        for FC_Variable, Name in FeatureClassGenerator(output_feature_dataset, "", "LINE", "NOT_RECURSIVE"):
            # Use the feature class name as the prefix for the exported shapefile
            _Name_shp = os.path.join(shapefile_output_folder, f"{Name}.shp")
            log(f"Exporting shapefile: {_Name_shp}")
     
            # Process: Export Features
            arcpy.conversion.ExportFeatures(
                in_features=FC_Variable,
                out_features=_Name_shp,
                field_mapping=(
                    "Elevation \"Elevation\" true true false 4 Long 0 0,First,#,"
                    f"{output_feature_dataset}\\{Name},Elevation,-1,-1;"
                    "Line_Type \"Line_Type\" true true false 20 Text 0 0,First,#,"
                    f"{output_feature_dataset}\\{Name},Line_Type,0,19;"
                    "Shape_Length \"Shape_Length\" false true true 8 Double 0 0,First,#,"
                    f"{output_feature_dataset}\\{Name},Shape_Length,-1,-1"
                )
            )
        
        # End of Export to shapefiles

    except Exception as e:
        log(f"An error occurred: {str(e)}")
    finally:
        # Check in licenses
        arcpy.CheckInExtension("3D")
        arcpy.CheckInExtension("spatial")
        log("Checked in 3D and Spatial Analyst extensions.")

        # Log total processing time
        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        hours, remainder = divmod(total_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        log(f"Total processing time: {int(hours)}h {int(minutes)}m {int(seconds)}s")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)  # Explicit success exit code
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Explicit failure exit code
