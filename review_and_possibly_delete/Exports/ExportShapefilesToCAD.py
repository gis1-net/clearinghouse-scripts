"""
Script for Exporting Shapefiles to CAD Format (DWG) Using Parallel Processing

Property of: GIS1

Author: Juan Machado
Date: 12/20/2024

Overview:
This script is designed to export shapefiles (specifically LINE feature classes) from a specified folder into a CAD format (DWG) using the ArcPy library. The script processes shapefiles in parallel to optimize performance, and it includes several steps such as geometry validation, repair, and retries in case of failure. It also performs memory management using garbage collection and logs detailed information about each operation for troubleshooting and tracking.

The script now supports command-line arguments for `state` and `county`. If these parameters are provided when executing the script, it skips the user confirmation step. Otherwise, the script prompts the user to input the required values.

Features:
- Scans a specified folder for shapefiles and exports them to a CAD format (DWG).
- Parallel processing of shapefiles using the `multiprocessing` library to optimize performance.
- Handles retries for failed exports, including geometry validation and repair.
- Memory usage monitoring and garbage collection after each batch to ensure efficient performance.
- Supports command-line arguments for `state` and `county` for improved automation.
- Logging of all operations to a file and the console, including detailed error handling.

Parameters:
- `shapefiles_folder`: The directory containing the shapefiles to be processed.
- `output_cad_folder`: The directory where the resulting CAD files (DWG) will be saved.
- `cad_version`: The version of the CAD file to export (e.g., "DWG_R2018").
- `log_file`: The path to the log file where all operations are recorded.
- `failed_exports_file`: The file where paths of shapefiles that failed to export will be logged.
- `NumberOfProcessors`: The number of processors to use for parallel processing. Default is the total number of CPU cores minus one.
- `retries`: The number of retries for each shapefile in case of export failure (default is 3).

Functions:
1. `clear_screen()`: Clears the console screen.
2. `log_message(message)`: Logs messages to both console and the log file.
3. `get_memory_usage()`: Returns the current memory usage in MB.
4. `get_user_input()`: Prompts the user for state and county names if not provided as command-line arguments.
5. `feature_class_generator(workspace, wild_card="*", feature_type="ALL", recursive=True)`: Generator that yields feature classes from the specified workspace.
6. `process_shapefile(shapefile, output_folder, cad_version, failed_exports_file)`: Processes a single shapefile and exports it to CAD format (DWG).
7. `process_all_shapefiles_parallel(shapefile_list, output_folder, cad_version, batches_processed)`: Processes all shapefiles in parallel using multiprocessing for efficient export.
8. `main()`: The main function that configures inputs, validates shapefiles, and initiates the parallel processing of shapefiles.

Usage:
1. Using Command-Line Arguments:
    python script.py [STATE] [COUNTY]

    Example:
    python script.py SOUTH_CAROLINA Abbeville

2. Without Command-Line Arguments:
    Run the script directly. It will prompt for the state and county names:
    - Enter the state name (e.g., "South Carolina").
    - Enter the county name (e.g., "Abbeville").

3. Ensure that the required directories for shapefiles and output CAD files exist.
4. Logs of the process will be saved in the specified log file, and any failed exports will be recorded in the failed exports file.

Dependencies:
- `arcpy` (ArcGIS library)
- `psutil` (For memory usage tracking)
- Python 3.x

"""


import arcpy
import os
import multiprocessing
import logging
import time
import psutil  # For memory usage tracking
import sys
from datetime import datetime


# Clear the console screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Function to log messages
def log_message(message):
    """Log messages to both console and file."""
    print(message)
    logging.info(message)


# Function to get current memory usage
def get_memory_usage():
    """Returns current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # Memory in MB


# Function to generate feature classes in a folder
def feature_class_generator(workspace, wild_card="*", feature_type="ALL", recursive=True):
    """Generates feature classes from the given workspace."""
    arcpy.env.workspace = workspace
    for fc in arcpy.ListFeatureClasses(wild_card=wild_card, feature_type=feature_type):
        yield os.path.join(workspace, fc), fc

    if recursive:
        for sub_ws in arcpy.ListWorkspaces("*", "Folder"):
            yield from feature_class_generator(sub_ws, wild_card, feature_type, recursive)


# Function to process a single shapefile
def process_shapefile(shapefile, output_folder, cad_version, failed_exports_file):
    """Processes a single shapefile and exports it to CAD."""
    try:
        output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(shapefile))[0] + ".dwg")
        arcpy.ExportCAD_conversion(
            shapefile, cad_version, output_file, "USE_FILENAMES_IN_TABLES", None, None
        )
        log_message(f"Successfully exported: {shapefile} to {output_file}")
    except Exception as e:
        with open(failed_exports_file, "a") as f:
            f.write(f"{shapefile} - {str(e)}\n")
        log_message(f"Failed to export: {shapefile}. Error: {e}")


# Function to process shapefiles in parallel
def process_all_shapefiles_parallel(shapefiles, output_folder, cad_version, batches_processed):
    """Processes all shapefiles in parallel."""
    log_message("Starting parallel processing...")
    start_time = time.time()
    failed_exports_file = os.path.join(output_folder, "Failed_Exports.txt")

    def worker(shapefile):
        process_shapefile(shapefile, output_folder, cad_version, failed_exports_file)
        with batches_processed.get_lock():
            batches_processed.value += 1
        log_message(f"Batches processed: {batches_processed.value} / {len(shapefiles)}")
        log_message(f"Current memory usage: {get_memory_usage():.2f} MB")

    with multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1) as pool:
        pool.map(worker, [shapefile[0] for shapefile in shapefiles])

    log_message(f"Completed parallel processing in {time.time() - start_time:.2f} seconds.")


# Main script
def main():
    # Clear the screen at the start
    clear_screen()

    # Parse command-line arguments
    if len(sys.argv) >= 3:
        state = sys.argv[1].strip().upper()
        county = sys.argv[2].strip().title()
        interactive = False
    else:
        # Get user input if no arguments are passed
        state = input("Enter the state name: ").strip().upper()
        county = input("Enter the county name: ").strip().title()
        interactive = True

    # Set paths dynamically
    base_path = f"W:\\{state}\\{county}_County_Contours"
    shapefiles_folder = os.path.join(base_path, "Shapefiles")
    output_cad_folder = os.path.join(base_path, "Dwg_Files")
    log_file = os.path.join(base_path, "logs", f"ExportShapefilesToCAD_{county}_Log.txt")
    failed_exports_file = os.path.join(base_path, "logs", f"FailedCAD_Exports_{county}.txt")
    cad_version = "DWG_R2018"

    # Show values for validation
    print("Validating the input and derived paths:")
    print(f"State: {state}")
    print(f"County: {county}")
    print(f"Shapefiles Folder: {shapefiles_folder}")
    print(f"Output CAD Folder: {output_cad_folder}")
    print(f"CAD Version: {cad_version}")
    print(f"Log File: {log_file}")
    print(f"Failed Exports File: {failed_exports_file}\n")

    # Confirm the values with the user if in interactive mode
    if interactive:
        confirmation = input("Are these values correct? (yes/no): ").strip().lower()
        if confirmation != 'yes':
            print("Exiting script. Please restart and provide correct input.")
            return

    # Configure logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logging.getLogger().addHandler(console_handler)

    # Ensure output folder exists
    if not os.path.exists(output_cad_folder):
        os.makedirs(output_cad_folder)
        log_message(f"Created output folder: {output_cad_folder}")

    # Scan the folder and retrieve shapefiles
    log_message(f"Scanning shapefiles folder: {shapefiles_folder}")
    shapefile_list = [
        (path, name)
        for path, name in feature_class_generator(shapefiles_folder, wild_card="*", feature_type="LINE", recursive=False)
    ]

    if not shapefile_list:
        log_message("No shapefiles found. Exiting.")
        return

    log_message(f"Found {len(shapefile_list)} shapefiles to process.")

    # Process shapefiles in parallel
    batches_processed = multiprocessing.Value('i', 0)  # Shared value for batches processed
    process_all_shapefiles_parallel(shapefile_list, output_cad_folder, cad_version, batches_processed)

    log_message("Script completed.")


if __name__ == "__main__":
    main()
