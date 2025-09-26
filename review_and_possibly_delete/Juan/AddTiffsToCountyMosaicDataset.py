"""
Script Name: Contour Processing and Smoothing Script
Created by: Juan Machado - GIS1.net
Date: 1/4/2025

Notes: Make sure you run it from the location of ESRI ArcPy needed:
                  cd "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\"
                  .\python.exe D:\scripts\contouring.py
                  
Description:
This script automates the processing of contour lines using ArcGIS. It performs the following tasks:

1. **Contour Generation**: Converts a raster mosaic dataset into contour lines with a specified interval and z-factor.
2. **Feature Layer Creation and Filtering**: Creates a feature layer from the contour lines and removes features based on specified criteria (e.g., Shape_Length < 5).
3. **Projection**: Reprojects the contour lines to a specified coordinate system.
4. **Line Smoothing**: Smooths the contour lines using the PAEK algorithm with a specified tolerance.
5. **Field Operations**: Adds and calculates fields such as Elevation and Line_Type for classification and reclassification.
6. **Field Cleanup**: Deletes unnecessary fields to optimize the output.
7. **Splitting Features**: Splits the smoothed contour lines based on a spatial index feature class and exports them to a specified workspace.

Inputs:
- **input_mosaic_dataset**: The path to the raster mosaic dataset used for generating contour lines.
- **output_feature_dataset**: The output workspace for the split and smoothed contour lines.
- **index_feature_class**: The index feature class used for splitting the contour lines.
- **contour_lines_sp**: The path for the projected contour lines.
- **smoothed_contour_lines**: The output path for the smoothed contour lines.

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
import sys

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
    
    log_dir = f"Z:\\{state_name}\\{county_name}_Contours"

    log_file = os.path.join(log_dir, "AddTiffsToCountyMosaicDataset.log")
    
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


# Main function
def main():
    clear_screen()
    start_time = datetime.datetime.now() 
    global state_name, county_name  # Declare global variables to update them
    
    # Parse state and county from command-line arguments or prompt the user
    if len(sys.argv) >= 4:
        state_name = sys.argv[1].strip()
        county_name = sys.argv[2].strip()
        elevation_units = sys.argv[3].strip()
        skip_confirmation = True  # Skip confirmation if parameters are passed
    else:
        state_name = input("Enter the State Name: ").strip()
        county_name = input("Enter the County Name: ").strip()
        elevation_units = input("Are DEM elevation values in feet or meters? (F/m): ").strip()

        skip_confirmation = False  # Require confirmation if no parameters are passed

    elevation_meters = elevation_units[0] == 'm' or elevation_units[0] == 'M'
    z_factor = 1
    if elevation_meters:
        z_factor = 3.280839895

    # Clear the log file at the start 
    log_dir = f"Z:\\{state_name}\\{county_name}_Contours"
    os.makedirs(log_dir, exist_ok=True)  # Ensure the directory exists
    log_file = os.path.join(log_dir, "AddTiffsToCountyMosaicDataset.log")
    if os.path.exists(log_file):
        os.remove(log_file)
    with open(log_file, "w") as f:
        pass  # Creates an empty log file



    # Now that state and county are defined, log the initial message
    log(f"Welcome to the Contour Processing Script.")
    log(f"Processing State: {state_name}, County: {county_name}")


    # Define input and output paths dynamically
    base_path = f"Z:\\{state_name}\\{county_name}_Contours"
    input_mosaic_dataset = os.path.join(base_path, "Contours_Step1.gdb", "Mosaic_Dataset_UTM" if elevation_meters else "Mosaic_Dataset_SP")

      
    tif_files_utm = os.path.join(base_path, "Tif_Files_UTM")

    
    
    
    # Log initial variables
    log("Initial variables:")
    log(f"  input_mosaic_dataset: {input_mosaic_dataset}")
    log(f"  tif_files_utm: {tif_files_utm}")
    
 
 


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
        
         # Setting this back to normal
        arcpy.env.parallelProcessingFactor = None



        

        # Add TIFFs to County Mosaic Dataset
        log("Adding TIFFs to County Mosaic Dataset.")
        
        arcpy.management.AddRastersToMosaicDataset(
            in_mosaic_dataset=input_mosaic_dataset,
            raster_type="Raster Dataset",
            input_path=tif_files_utm,
            sub_folder="NO_SUBFOLDERS", 
            duplicate_items_action="EXCLUDE_DUPLICATES"
        )
        log("TIFFs added to County Mosaic Dataset.")
        
        # Clear all workspace caches to release locks
        # ESRI BUG-000160515
        arcpy.ClearWorkspaceCache_management()
        
        
        
   

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
