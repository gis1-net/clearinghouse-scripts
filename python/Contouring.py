"""
Script Name: Contour Processing Script
Created by: Nick Rupert, Chad Rupert, and Juan Machado - GIS1.net
Date: September 5, 2025

Notes: Make sure you run it from the location of ESRI ArcPy needed:
    python Z:\Clearinghouse_Support\python\Contouring.py
                  
Description:
This script automates the processing of contour lines using ArcGIS. It performs the following tasks:

Outputs:
- Various feature classes and layers representing processed and smoothed contour lines.

Dependencies:
- Requires ArcGIS Pro and licenses for 3D Analyst and Spatial Analyst extensions.

Usage:
- Ensure the input paths and parameters are correctly defined before running the script.
- Execute the script in an environment with ArcGIS Pro installed and the necessary licenses checked out.

1. Using Command-Line Arguments:
    python Z:\Clearinghouse_Support\python\Contouring.py [STATE] [COUNTY] [CRS]

    Example:
    python Z:\Clearinghouse_Support\python\Contouring.py.py SOUTH_CAROLINA Abbeville_County 6570

2. Without Command-Line Arguments:
    Run the script directly. It will prompt for the state and county names:
    - Enter the state name (e.g., "SOUTH_CAROLINA").
    - Enter the county name (e.g., "Abbeville_Couty").
    - Enter the ID # of the target output state plane coordinate system (e.g. 6570 for South Carolina SP).

Notes:
- This script overwrites existing output files if they already exist.
- Modify the coordinate system or other parameters as needed for specific datasets.
"""

import arcpy
import os
import datetime
import subprocess
import traceback
import json

#region Config Vars
DATA_DRIVE = 'Z'
LOG_FILE = 'contouring.log'
Z_FACTOR_METERS = 3.280839895
Z_FACTOR_FEET = 1
CONTOUR_INTERVAL = 1
SMOOTH_ENABLED = False
MAX_FEATURE_VERTICES = 500000
MIN_ATTRIBUTE_LENGTH = 5
SMOOTH_ALGORITHM = "PAEK"
SMOOTH_TOLERANCE = "10 Feet"
CONTOUR_SPLIT_FIELD = "TILE_NUM"
NO_DATA_VALUE = -999999

SHAPEFILE_AUX_EXTENSIONS = [".shp.xml", ".sbx", ".sbn", ".cpg"]
DWG_AUX_EXTENSIONS = [".dwg.xml"]

ARCPY_OVERWRITE_INPUT = True

# region Path/File Names
CONTOURS_WIP_GEODATABASE = "Contour_Lines_WIP.gdb"
CONTOURS_WIP_SP_GEODATABASE = "Contour_Lines_WIP_SP.gdb"
MOSAIC_DATASET = 'Mosaic_Dataset'
CONTOURS_FEATURE_CLASS = "Contour_Lines"
CONTOURS_SP_FEATURE_DATASET = "Contour_Lines_SP"
MOSAIC_BOUNDARY_FEATURE_CLASS = "Mosaic_Boundary"
MOSAIC_BOUNDARY_SP_FEATURE_CLASS = "Mosaic_Boundary_SP"
TIF_FILES = "Tif_Files_UTM"

CONTOUR_TILES_FEATURE_DATASET = "Contour_Tiles"
TILE_INDEX_FEATURE_DATASET = "Index_5000Ft"
TILE_INDEX_W_LIMITS_FEATURE_CLASS = "Index_5000Ft_w_Limits"
TILE_INDEX_WGS_FEATURE_CLASS = "Index_5000Ft_WGS"
DATA_LIMITS_FEATURE_CLASS = "Data_Limits"
DATA_LIMITS_SP_FEATURE_CLASS = "Data_Limits_SP"

CONTOURS_INDEX_JSON = "Contours_Index.geojson"

SHAPEFILE_OUTPUT_FOLDER = 'Shapefiles'
DWG_OUTPUT_FOLDER = 'Dwg_Files'
#endregion
#endregion

#region Global Input Vars
MODE = None
STATE = None
LOCALITY = None
TARGET_SP_COORDINATE_SYSTEM = None
BASE_DIR = None
OUTPUT_GEODATABASE = None
COORDINATE_SYSTEM_IS_METERS = None
Z_FACTOR = None
#endregion

#region Utility Functions
def clear_screen():
    """Clears the terminal window"""
    subprocess.call("cls", shell=True)
       
def clear_log():
    """Clear messages from log file, if any"""
    os.makedirs(BASE_DIR, exist_ok=True)  # Ensure the directory exists
    log_file = os.path.join(BASE_DIR, LOG_FILE)
    if os.path.exists(log_file):
        os.remove(log_file)
    with open(log_file, "w") as f:
        pass  # Creates an empty log file

def log(message):
    """Print a log message to the console and to a log file"""

    if not BASE_DIR:
        raise ValueError("State and County names must be defined before logging.")

    log_file = os.path.join(BASE_DIR, LOG_FILE)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"

    # Print to console
    print(formatted_message)

    # Write to log file
    try:
        os.makedirs(BASE_DIR, exist_ok=True)  # Ensure directory exists
        with open(log_file, "a") as file:  # Append mode
            file.write(formatted_message + "\n")
            file.flush()
    except Exception as e:
        print(f"Failed to write log to {log_file}: {e}")

def log_time(start_time, end_time):
    """Log the total execution time"""

    total_time = end_time - start_time
    hours, remainder = divmod(total_time.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    log(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Total processing time: {int(hours)}h {int(minutes)}m {int(seconds)}s")

def clear_folder_contents(path):
    """
    Deletes all files and subdirectories in the given folder.
    Reports total files deleted, and logs any errors (e.g., .lock files).
    """
    files_deleted = 0
 
    if not os.path.exists(path):
        log(f"Folder not found: {path}")
        return 0
 
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                files_deleted += 1
            except Exception as e:
                log(f"Error deleting file: {file_path} — {e}")
 
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rmdir(dir_path)
            except OSError as e:
                log(f"Error removing folder: {dir_path} — {e}")
 
    log(f"Total files deleted from {path}: {files_deleted}")
    return files_deleted

def get_inputs():
    """In interactive mode, ask questions and collect inputs from the CLI"""

    global MODE, STATE, LOCALITY, TARGET_SP_COORDINATE_SYSTEM, BASE_DIR, OUTPUT_GEODATABASE, SHAPEFILE_OUTPUT_FOLDER, DWG_OUTPUT_FOLDER

    # Parse state, locality, and elevation units from command-line arguments or prompt the user
    if len(sys.argv) >= 4:
        MODE = "passive"  # Skip confirmation if parameters are passed
        STATE = sys.argv[1].strip()
        LOCALITY = sys.argv[2].strip()
        TARGET_SP_COORDINATE_SYSTEM = sys.argv[3].strip()
    else:
        MODE = "interactive"  # Require confirmation if no parameters are passed
        STATE = input("Enter the State Folder Name: ").strip()
        LOCALITY = input("Enter the Locality Folder Name: ").strip()
        TARGET_SP_COORDINATE_SYSTEM = input("Enter the ID # of the target output state plane coordinate system (e.g. 6570 for South Carolina SP): ")

    BASE_DIR = os.path.join(f'{DATA_DRIVE}:', STATE, f'{LOCALITY}_Contours')
    OUTPUT_GEODATABASE = f'{LOCALITY}_Contours.gdb'

#endregion

#region ArcPy Helper Functions
def setup_arcpy():
    """Set environment variables and check out necessary licenses for ArcPy"""

    # Set environment variables
    arcpy.env.overwriteOutput = ARCPY_OVERWRITE_INPUT
    log(f"Environment overwriteOutput set to {ARCPY_OVERWRITE_INPUT}.")

    # Check out necessary licenses
    arcpy.CheckOutExtension("3D")
    arcpy.CheckOutExtension("spatial")
    log("Checked out 3D and Spatial Analyst extensions.")

def cleanup_arcpy():
    """Check in necessary ArcPy licenses at the end of the script execution"""

    arcpy.CheckInExtension("3D")
    arcpy.CheckInExtension("spatial")
    log("Checked in 3D and Spatial Analyst extensions.")

def delete_all_feature_classes_in_dataset(dataset_path):
    """
    Deletes all feature classes within the specified feature dataset.
    Parameters:
        dataset_path (str): Full path to the feature dataset (.gdb\FeatureDataset)
    Returns:
        int: Number of feature classes successfully deleted
    """
    if not arcpy.Exists(dataset_path):
        log(f"Dataset not found: {dataset_path}")
        return 0
 
    arcpy.env.overwriteOutput = False
    deleted_count = 0
 
    with arcpy.EnvManager(workspace=dataset_path):
        featureclasses = arcpy.ListFeatureClasses()
 
        for fc in featureclasses:
            fc_path = os.path.join(dataset_path, fc)
            try:
                arcpy.management.Delete(fc_path)
                deleted_count += 1
            except Exception as e:
                log(f"Error deleting {fc_path}: {e}")
 
    log(f"Deleted {deleted_count} feature classes from: {dataset_path}")
    return deleted_count
 
def arcpy_delete(path):
    """Deletes a feature class"""

    if arcpy.Exists(path):
        log(f"Feature class exists: {path}, deleting...")
        
        # Attempt to delete the feature class
        Delete_Succeeded = arcpy.management.Delete(in_data=[path])[0]
        
        # Confirm deletion
        if not arcpy.Exists(path):
            log(f"Successfully deleted: {path}")
        else:
            log(f"Deletion failed: {path}")
    else:
        log(f"Feature class does not exist: {path}")

def generate_feature_class(workspace, wild_card, feature_type, recursive):
    """Creates a feature class"""

    with arcpy.EnvManager(workspace=workspace):
        dataset_list = [""]
        if recursive:
            datasets = arcpy.ListDatasets()
            dataset_list.extend(datasets)
 
        for dataset in dataset_list:
            featureclasses = arcpy.ListFeatureClasses(wild_card, feature_type, dataset)
            for fc in featureclasses:
                yield os.path.join(workspace, dataset, fc), fc

def read_mosaic_dataset_crs(mosaic_dataset):
    """Reads the coordinate reference system of the given mosaic dataset"""

    raster = arcpy.Raster(mosaic_dataset)
    return raster.spatialReference

#endregion

#region Contour Line Processing Steps
def intro_message():
    """
    Print the introduction message and information at the beginning of the script
    If in interactive mode, confirm before proceeding
    """

    log(f"Welcome to the Contour Processing Script.")
    log(f"Processing State: {STATE}, County: {LOCALITY}")
    
    if MODE == 'interactive':
        proceed = input("Do you want to proceed with the script? (y/n): ").strip().lower()
        if proceed[0] != 'y':
            log("Script execution cancelled by user.")
            return

def cleanup_old_contours_files():
    """
    Delete all previous Legacy, Work-In-Progress, and Output files related to contour lines from previous executions
    """

    # Delete legacy Geodatabases if any
    work_in_progress_geodatabase = os.path.join(BASE_DIR, "Contours_Work_In_Progress.gdb")
    log(f"Deleting previous work_in_progress geodatabase, if any: {work_in_progress_geodatabase}")
    arcpy_delete(work_in_progress_geodatabase)

    step_1_geodatabase = os.path.join(BASE_DIR, "Contours_Work_In_Progress.gdb")
    log(f"Deleting previous step 1 geodatabase, if any: {step_1_geodatabase}")
    arcpy_delete(step_1_geodatabase)

    step_2_geodatabase = os.path.join(BASE_DIR, "Contours_Work_In_Progress.gdb")
    log(f"Deleting previous step 2 geodatabase, if any: {step_2_geodatabase}")
    arcpy_delete(step_2_geodatabase)

    step_3_geodatabase = os.path.join(BASE_DIR, "Contours_Work_In_Progress.gdb")
    log(f"Deleting previous step 3 geodatabase, if any: {step_3_geodatabase}")
    arcpy_delete(step_3_geodatabase)

    # Delete mosaic dataset if any
    mosaic_dataset = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE, MOSAIC_DATASET)
    log(f"Deleting previous mosaic dataset, if any: {mosaic_dataset}")
    arcpy_delete(mosaic_dataset)

    # Delete contours elev ft if any present
    initial_contours = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE, CONTOURS_FEATURE_CLASS)
    log(f"Deleting previous contours elev ft file, if any: {initial_contours}")
    arcpy_delete(initial_contours)

    # Ensure there is no Contours_Line_SP created from an old model
    contour_lines_sp_feature_class = os.path.join(BASE_DIR, CONTOURS_WIP_SP_GEODATABASE, CONTOURS_SP_FEATURE_DATASET)
    log(f"Deleting Contour Lines (SP) Feature Class: {contour_lines_sp_feature_class}")
    arcpy_delete(contour_lines_sp_feature_class)
    
    # Delete any files in the DWG and Shapefiles output folders
    shapefile_output_folder = os.path.join(BASE_DIR, SHAPEFILE_OUTPUT_FOLDER)
    log(f"Deleting previous files from Shapefile output folder, if any: {shapefile_output_folder}")

    dwg_output_folder = os.path.join(BASE_DIR, DWG_OUTPUT_FOLDER)
    clear_folder_contents(shapefile_output_folder)
    log(f"Deleting previous files from DWG output folder, if any: {dwg_output_folder}")
    clear_folder_contents(dwg_output_folder)

    # Delete all feature classes in output_feature_dataset, if any present
    output_feature_dataset = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, CONTOUR_TILES_FEATURE_DATASET)
    log(f"Deleting all feature classes in output_feature_dataset, if any: {output_feature_dataset}")
    delete_all_feature_classes_in_dataset(output_feature_dataset)
    
def cleanup_old_index_files():
    """Delete all previous Work-In-Progress and Output files related to the contour tile index from previous executions"""

    # Ensure there is no Boundary_UTM from an old model
    mosaic_boundary = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, "Mosaic_Boundary")
    log(f"Deleting Boundary UTM from old models, if any: {mosaic_boundary}")
    arcpy_delete(mosaic_boundary)
    
    # Delete all mosaic boundary files, if any present
    mosaic_boundary = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, MOSAIC_BOUNDARY_FEATURE_CLASS)
    log(f"Deleting previous mosaic boundary files, if any: {mosaic_boundary}")
    arcpy_delete(mosaic_boundary)

    # Delete all mosaic boundary SP files, if any present
    mosaic_boundary_sp = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, MOSAIC_BOUNDARY_SP_FEATURE_CLASS)
    log(f"Deleting previous mosaic boundary sp files, if any: {mosaic_boundary_sp}")
    arcpy_delete(mosaic_boundary_sp)

    # Delete all data limit file, if any present
    data_limits = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, DATA_LIMITS_FEATURE_CLASS)
    log(f"Deleting previous data limits file, if any: {data_limits}")
    arcpy_delete(data_limits)

    # Delete data limit sp if any present
    data_limits_sp = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, DATA_LIMITS_SP_FEATURE_CLASS)
    log(f"Deleting previous data limits sp file, if any: {data_limits_sp}")
    arcpy_delete(data_limits_sp)

    # Delete tile index with limits if any present
    tile_index_w_limits = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, TILE_INDEX_W_LIMITS_FEATURE_CLASS)
    log(f"Deleting previous WGS tile index file, if any: {tile_index_w_limits}")
    arcpy_delete(tile_index_w_limits)

    # Delete tile index WGS if any present
    tile_index_wgs = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, TILE_INDEX_WGS_FEATURE_CLASS)
    log(f"Deleting previous WGS tile index file, if any: {tile_index_wgs}")
    arcpy_delete(tile_index_wgs)

    # Delete geojson index if present
    boundary_geojson = os.path.join(BASE_DIR, f"{LOCALITY}_{CONTOURS_INDEX_JSON}")
    log(f"Deleting previous GeoJSON index file, if any: {boundary_geojson}")
    arcpy_delete(boundary_geojson)
    
def compact_contours_wip_geodatabase():
    """Compact the contours geodatabase"""

    # Intermediate compaction of the county contours geodatabase
    # (This geodatabase is reused later for exporting and further processing)
    contours_wip_geodatabase = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE)
    log(f"Compacting geodatabase: {contours_wip_geodatabase}")
    arcpy.Compact_management(contours_wip_geodatabase)
    log("Intermediate geodatabase compaction completed.")

def create_structure():
    """Create any missing paths or files"""

    contours_wip_geodatabase = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE)
    if not arcpy.exists(contours_wip_geodatabase):
        log(f"Creating Contours Geodatabase {contours_wip_geodatabase}")
        arcpy.management.CreateFileGDB(
            out_folder_path=BASE_DIR,
            out_name=CONTOURS_WIP_GEODATABASE
        )

    contours_feature_class = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE, CONTOURS_FEATURE_CLASS)
    if not arcpy.exists(contours_feature_class):
        log(f"Creating Contours Feature Class {contours_feature_class}")
        arcpy.management.CreateFeatureClass(
            out_path=os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE),
            out_name='Contours'
        )

    output_geodatabase = os.path.join(BASE_DIR, OUTPUT_GEODATABASE)
    if not arcpy.exists(output_geodatabase):
        log(f"Creating Contours Geodatabase {output_geodatabase}")
        arcpy.management.CreateFileGDB(
            out_folder_path=BASE_DIR,
            out_name=OUTPUT_GEODATABASE
        )

    tiles_feature_dataset = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, TILE_INDEX_FEATURE_DATASET)
    if not arcpy.exists(tiles_feature_dataset):
        log(f"Creating Tiles Feature Dataset {tiles_feature_dataset}")
        arcpy.management.CreateFeatureDataset(
            out_dataset_path=os.path.join(BASE_DIR, OUTPUT_GEODATABASE),
            out_name=TILE_INDEX_FEATURE_DATASET,
            spatial_reference=TARGET_SP_COORDINATE_SYSTEM
        )

def set_tif_nodata_values():
    """Set standard NoData value for all .tif files"""

    tif_files_dir = os.path.join(BASE_DIR, TIF_FILES)
    tif_files = os.listdir(tif_files_dir)

    for f in tif_files:
        file_path = os.path.join(tif_files_dir, f)
        if os.path.isfile(file_path) and f.endswith('.tif'):
            log(f'Setting {file_path} NoData value to {NO_DATA_VALUE}')
            arcpy.management.SetRasterProperties(in_raster=file_path, nodata=f'1 {NO_DATA_VALUE}')

def create_mosaic_dataset(mosaic_dataset):
    """Create mosaic dataset from Tif Files"""

    mosaic_dataset = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE, MOSAIC_DATASET)

    tif_files_dir = os.path.join(BASE_DIR, TIF_FILES)
    example_tif_file = [f for f in os.listdir(tif_files_dir) if os.path.isfile(os.path.join(tif_files_dir, f)) and f.endswith('.tif')][0]

    tif_coordinate_system = arcpy.Describe(os.path.join(tif_files_dir, example_tif_file)).spatialReference

    log(f'Creating mosaic dataset {mosaic_dataset}')
    arcpy.management.CreateMosaicDataset(
        in_workspace=os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE),
        in_mosaicdataset_name=MOSAIC_DATASET,
        coordinate_system=tif_coordinate_system
    )

    log(f'Adding rasters from {tif_files_dir} to mosaic dataset {mosaic_dataset}')
    arcpy.management.AddRastersToMosaicDataset(
        in_mosaic_dataset=mosaic_dataset,
        raster_type='Raster Dataset',
        input_path=tif_files_dir
    )

def calculate_contours_raster_statistics(input_path):
    """Calculate raster statistics on mosaic dataset"""

    # Set this to ZERO so LocalWorker.exe doesn't go crazy
    arcpy.env.parallelProcessingFactor = 0
    log(f"Environment parallelProcessingFactor set to 0.")

    log("Calculating raster statistics...")
    arcpy.management.CalculateStatistics(input_path)
    log("Raster statistics calculated.")

    # Set this back to normal
    arcpy.env.parallelProcessingFactor = None
    log(f"Environment parallelProcessingFactor set to None.")

# Step 1
def generate_contours(input_path, output_path):
    """Generate contour lines from mosaic dataset"""

    log("Starting Contour process.")
    arcpy.ddd.Contour(
        in_raster=input_path,
        out_polyline_features=output_path,
        contour_interval=CONTOUR_INTERVAL,
        z_factor=Z_FACTOR,
        max_vertices_per_feature=MAX_FEATURE_VERTICES
    )
    log(f"Contour process completed. Output: {output_path}")

# Step 2
def filter_contours(input_path):
    """"""
    
    # Select Layer By Attribute
    min_length = MIN_ATTRIBUTE_LENGTH * (Z_FACTOR_METERS / Z_FACTOR)

    log(f"Selecting features with Shape_Length < {min_length}.")
    selected_layer, count = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=input_path, 
        where_clause=f"Shape_Length < {min_length}"
    )
    log(f"Selected {count} features.")

    # Delete Features
    log("Deleting selected features.")
    arcpy.management.DeleteFeatures(selected_layer)
    log("Selected features deleted.")

# Step 3
def project_contours(input_path, output_path):
    if not arcpy.exists(os.path.join(BASE_DIR, CONTOURS_WIP_SP_GEODATABASE)):
        log("Creating Geodatabase for projected contours")
        arcpy.management.CreateFileGDB(
            out_folder_path=BASE_DIR,
            out_name=CONTOURS_WIP_SP_GEODATABASE
        )

    if not arcpy.exists(os.path.join(BASE_DIR, CONTOURS_WIP_SP_GEODATABASE, CONTOURS_SP_FEATURE_DATASET)):
        log("Creating Feature Dataset for projected contours")
        arcpy.management.CreateFeatureDataset(
            out_dataset_path=os.path.join(BASE_DIR, CONTOURS_WIP_SP_GEODATABASE),
            out_name=CONTOURS_SP_FEATURE_DATASET,
            spatial_reference=TARGET_SP_COORDINATE_SYSTEM
        )

    log("Projecting contour lines.")
    arcpy.management.Project(
        in_dataset=input_path,
        out_dataset=output_path,
        # NOTE: out_coor_system is not used because out_dataset is a FeatureDataSet that has a pre-defined coordinate system that overrides any input
        # However, the function requires a valid coordinate system be provided as an argument
        out_coor_system=TARGET_SP_COORDINATE_SYSTEM
    )
    log(f"Projection completed. Output: {output_path}")
    
    log("Recalculating Feature Class Extent.")
    arcpy.management.RecalculateFeatureClassExtent(
        in_features=output_path
    )
    log(f"Recalculation of Feature Class Extent completed. Output: {output_path}")
 
    log("Repairing Geometry.")
    arcpy.management.RepairGeometry(
        in_features=output_path
    )
    log(f"Repairing of Geometry completed. Output: {output_path}")

# Step 4
def smooth_contours(input_path, output_path):
    log("Smoothing contour lines.")
    arcpy.cartography.SmoothLine(
       in_features=input_path,
       out_feature_class=output_path,
       algorithm=SMOOTH_ALGORITHM,
       tolerance=SMOOTH_TOLERANCE,
       error_option="RESOLVE_ERRORS" 
    )
    log(f"Smooth Line process completed. Output: {output_path}")

# Step 5
def add_contours_data_fields(input_path):
    log("Adding and calculating Elevation field.")
    arcpy.management.AddField(
        in_table=input_path,
        field_name="Elevation",
        field_type="LONG"
    )
    arcpy.management.CalculateField(
        in_table=input_path,
        field="Elevation",
        expression="!Contour!"
    )
    log("Field added and calculated.")

    # Add Line_Type Field and Reclassify
    # Define the function separately for better readability
    reclass_code = """def reclass(Elevation):
        if Elevation % 10 == 0:
            return 'Index-10'
        elif Elevation % 2 == 0:
            return 'Intermediate-2'
        else:
            return 'Intermediate-1'
    """

    # Add Line_Type Field and Reclassify
    log("Adding and calculating Line_Type field.")

    arcpy.management.AddField(
        in_table=input_path,
        field_name="Line_Type",
        field_type="TEXT",
        field_length=20
    )

    arcpy.management.CalculateField(
        in_table=input_path,
        field="Line_Type",
        expression="reclass(!Elevation!)",
        expression_type="PYTHON3",
        code_block=reclass_code
    )

    log("Line_Type field reclassified.")

# Step 6
def cleanup_contours_data_fields(input_path):
    log("Deleting unnecessary fields.")
    arcpy.management.DeleteField(
        in_table=input_path, 
        drop_field=["Id", "Contour", "InLine_FID"]
    )
    log("Fields deleted.")

# Step 7
def split_contours(input_path, output_path, split_path, split_field):
    log("Splitting contour lines.")
    arcpy.analysis.Split(
        in_features=input_path,
        split_features=split_path,
        split_field=split_field,
        out_workspace=output_path
    )
    log(f"Split process completed. Output workspace: {output_path}")

    return output_path

# Step 9
def export_contours_tiles(input_path):
    log("Iterating through all line feature classes in the specified dataset.")
        
    # Initialize counters
    shapefiles_1ft_count = 0
    shapefiles_2ft_count = 0
    dwg_1ft_count = 0
    dwg_2ft_count = 0
    multipart_to_singlepart_count = 0
    orig_fid_deleted_count = 0
    geometry_recalculated_count = 0
        
    log("Starting export and processing of shapefiles and DWGs...")

    shapefile_output_folder = os.path.join(BASE_DIR, SHAPEFILE_OUTPUT_FOLDER)
    if not os.path.exists(shapefile_output_folder):
        os.makedirs(shapefile_output_folder)

    dwg_output_folder = os.path.join(BASE_DIR, DWG_OUTPUT_FOLDER)
    if not os.path.exists(dwg_output_folder):
        os.makedirs(dwg_output_folder)
        
    for FC_Variable, Name in generate_feature_class(input_path, "", "LINE", "NOT_RECURSIVE"):
        
        shp_1ft_path = os.path.join(shapefile_output_folder, f"{Name}_1Ft.shp")
        
        # Multipart To Singlepart
        arcpy.management.MultipartToSinglepart(in_features=FC_Variable, out_feature_class=shp_1ft_path)
        multipart_to_singlepart_count += 1
        
        # Delete ORIG_FID
        shp_1ft_temp = arcpy.management.DeleteField(in_table=shp_1ft_path, drop_field=["ORIG_FID"])[0]
        orig_fid_deleted_count += 1
        
        # Recalculate Geometry
        arcpy.management.CalculateGeometryAttributes(
            shp_1ft_temp,
            [["Shape_Leng", "LENGTH"]],
            length_unit="FEET_US"
        )
        geometry_recalculated_count += 1
        
        # Export DWG 1Ft
        dwg_1ft_path = os.path.join(dwg_output_folder, f"{Name}_1Ft.dwg")
        arcpy.conversion.ExportCAD(
            in_features=shp_1ft_temp,
            Output_Type="DWG_R2018",
            Output_File=dwg_1ft_path
        )
        dwg_1ft_count += 1
        shapefiles_1ft_count += 1
        
        # Create Feature Layer and Select for 2Ft
        output = f"{Name}_1Ft_Layer"
        arcpy.management.MakeFeatureLayer(in_features=shp_1ft_temp, out_layer=output)
        
        shp_2ft_path = os.path.join(shapefile_output_folder, f"{Name}_2Ft.shp")
        arcpy.analysis.Select(
            in_features=output,
            out_feature_class=shp_2ft_path,
            where_clause="Line_Type = 'Index-10' Or Line_Type = 'Intermediate-2'"
        )
        shapefiles_2ft_count += 1
        
        # Export DWG 2Ft
        dwg_2ft_path = os.path.join(dwg_output_folder, f"{Name}_2Ft.dwg")
        arcpy.conversion.ExportCAD(
            in_features=shp_2ft_path,
            Output_Type="DWG_R2018",
            Output_File=dwg_2ft_path
        )
        dwg_2ft_count += 1
        
    # Final summary log
    log(f"Completed Multipart to Singlepart conversions: {multipart_to_singlepart_count}")
    log(f"Deleted ORIG_FID fields: {orig_fid_deleted_count}")
    log(f"Recalculated geometry attributes: {geometry_recalculated_count}")
    log(f"Exported {shapefiles_1ft_count} shapefiles (1Ft)")
    log(f"Exported {shapefiles_2ft_count} shapefiles (2Ft)")
    log(f"Exported {dwg_1ft_count} DWG files (1Ft)")
    log(f"Exported {dwg_2ft_count} DWG files (2Ft)")

# Step 10
def cleanup_contours_auxiliary_files(path, extensions):
    log(f"Cleaning up auxiliary files ({', '.join(extensions)}) in the output path {path}")

    deleted_files = 0

    for root, _, files in os.walk(path):
        for file in files:
            # Check if the file has one of the auxiliary extensions
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception as e:
                    log(f"Failed to delete {file_path}: {e}")

    log(f"Cleanup completed. Total auxiliary files deleted: {deleted_files}.")
#endregion

#region Boundary Index Processing Steps
# Step 1
def create_boundary_mosaic_dataset_nodata(input_path):
    log("Defining mosaic dataset NoData values")
    md_nodata = arcpy.management.DefineMosaicDatasetNoData(
        input_path, 
        num_bands=1, 
        bands_for_nodata_value=[["ALL_BANDS", NO_DATA_VALUE]]
    )[0]

    return md_nodata
        
# Step 2
def build_boundary_footprints(input_path):
    log("Building mosaic dataset footprints")
    output = arcpy.management.BuildFootprints(
        input_path,
        reset_footprint="RADIOMETRY",  # Computational Method: Radiometry
        min_data_value=-300,  # Minimum Data Value
        max_data_value=25000,  # Maximum Data Value
        approx_num_vertices=5000,  # Approximate Number of Vertices
        shrink_distance=0,  # Shrink Distance
        skip_derived_images=True,  # Skip Overviews: Yes
        update_boundary=True,  # Update Boundary: Yes
        simplification_method="NONE",  # Simplification Method: None
        request_size=2000,  # Request Size
        min_thinness_ratio=0.05,  # Minimum Thinness Ratio
        max_sliver_size=20,  # Maximum Sliver Size
        min_region_size=1  # Minimum Region Size
    )[0]

    return output

# Step 3
def export_boundary_mosaic_dataset(input_path, output_path):
    log("Exporting mosaic boundary geometry")
    arcpy.management.ExportMosaicDatasetGeometry(input_path, output_path)

# Step 4
def project_boundary_sp(input_path, output_path, spatial_reference):
    log(f"Projecting to {spatial_reference.name}")
    arcpy.management.Project(input_path, output_path, spatial_reference)

# Step 5
def intersect_boundary(input_path, index_path, output_path):
    log("Intersecting boundaries with index")
    arcpy.analysis.Intersect([[input_path, ""], [index_path, ""]], output_path)

# Step 6
def dissolve_boundary_features(input_path, output_path):
    # Process 6: Dissolve Features
    log("Dissolving data limits")
    arcpy.management.Dissolve(input_path, output_path)

# Step 7
def clip_boundary_features(input_path, clip_path, output_path):
    log("Clipping index features")
    arcpy.analysis.Clip(input_path, clip_path, output_path)

# Step 8
def cleanup_boundary_data_fields(input_path):
    log("Cleaning up fields")
    fields_to_delete = ["LABEL_X", "LABEL_Y", "NAME_X", "NAME_Y"]
    output = arcpy.management.DeleteField(input_path, fields_to_delete)[0]

    return output

# Step 9
def project_boundary_wgs84(input_path, output_path):
    log("Projecting to WGS84")
    arcpy.management.Project(input_path, output_path, 4326)  # WGS84

# Step 10
def export_boundary_geojson(input_path, output_path):
    log("Generating final GeoJSON")
    arcpy.conversion.FeaturesToJSON(
        input_path, 
        output_path, 
        geoJSON="GEOJSON"
    )

#endregion

#region Processes
def process_contour_lines():
    global COORDINATE_SYSTEM_IS_METERS, Z_FACTOR

    cleanup_old_contours_files()
    compact_contours_wip_geodatabase()

    mosaic_dataset = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE, MOSAIC_DATASET)
    set_tif_nodata_values()
    create_mosaic_dataset(mosaic_dataset)

    coordinate_system = read_mosaic_dataset_crs(mosaic_dataset)
    COORDINATE_SYSTEM_IS_METERS = coordinate_system.linearUnitName == 'Meter'
    Z_FACTOR = Z_FACTOR_METERS if (COORDINATE_SYSTEM_IS_METERS) else Z_FACTOR_FEET
    log(f'Coordinate system unit is {coordinate_system.linearUnitName}, Z-Factor set to {Z_FACTOR}')

    calculate_contours_raster_statistics(mosaic_dataset)

    initial_contours_feature_class = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE, CONTOURS_FEATURE_CLASS)
    generate_contours(input_path=mosaic_dataset, output_path=initial_contours_feature_class)

    contours_feature_class = initial_contours_feature_class

    filter_contours(input_path=contours_feature_class)

    if COORDINATE_SYSTEM_IS_METERS:
        projected_contours_feature_class = os.path.join(BASE_DIR, CONTOURS_WIP_SP_GEODATABASE, CONTOURS_SP_FEATURE_DATASET)
        project_contours(input_path=contours_feature_class, output_path=projected_contours_feature_class)
        contours_feature_class = projected_contours_feature_class

    # if SMOOTH_ENABLED:
    #     smooth_contours()
    
    add_contours_data_fields(input_path=contours_feature_class)
    cleanup_contours_data_fields(input_path=contours_feature_class)

    contour_tiles_feature_dataset = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, CONTOUR_TILES_FEATURE_DATASET)
    tile_index = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, TILE_INDEX_FEATURE_DATASET)
    split_contours(input_path=contours_feature_class, output_path=contour_tiles_feature_dataset, split_path=tile_index, split_field=CONTOUR_SPLIT_FIELD)
    
    export_contours_tiles(input_path=contour_tiles_feature_dataset)
    cleanup_contours_auxiliary_files(os.path.join(BASE_DIR, SHAPEFILE_OUTPUT_FOLDER), SHAPEFILE_AUX_EXTENSIONS)
    cleanup_contours_auxiliary_files(os.path.join(BASE_DIR, DWG_OUTPUT_FOLDER), DWG_AUX_EXTENSIONS)

def process_boundary_index():
    cleanup_old_index_files()

    input_mosaic_dataset = os.path.join(BASE_DIR, CONTOURS_WIP_GEODATABASE, MOSAIC_DATASET)

    mosaic_dataset_nd = create_boundary_mosaic_dataset_nodata(input_mosaic_dataset)
    footprint = build_boundary_footprints(input_path=mosaic_dataset_nd)

    mosaic_boundary = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, MOSAIC_BOUNDARY_FEATURE_CLASS)
    export_boundary_mosaic_dataset(input_path=footprint, output_path=mosaic_boundary)

    if COORDINATE_SYSTEM_IS_METERS:
        coordinate_system = read_mosaic_dataset_crs(input_mosaic_dataset)
        projected_mosaic_boundary = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, MOSAIC_BOUNDARY_SP_FEATURE_CLASS)
        project_boundary_sp(input_path=mosaic_boundary, output_path=projected_mosaic_boundary, spatial_reference=coordinate_system)
        mosaic_boundary = projected_mosaic_boundary

    tile_index_path = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, TILE_INDEX_FEATURE_DATASET)

    intersect = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, DATA_LIMITS_FEATURE_CLASS)
    intersect_boundary(input_path=mosaic_boundary, index_path=tile_index_path, output_path=intersect)

    dissolved = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, DATA_LIMITS_SP_FEATURE_CLASS)
    dissolve_boundary_features(input_path=intersect, output_path=dissolved)

    clipped = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, TILE_INDEX_W_LIMITS_FEATURE_CLASS)
    clip_boundary_features(input_path=tile_index_path, clip_path=dissolved, output_path=clipped)

    cleaned = cleanup_boundary_data_fields(input_path=clipped)

    index_wgs = os.path.join(BASE_DIR, OUTPUT_GEODATABASE, TILE_INDEX_WGS_FEATURE_CLASS)
    project_boundary_wgs84(input_path=cleaned, output_path=index_wgs)

    boundary_geojson = os.path.join(BASE_DIR, f"{LOCALITY}_{CONTOURS_INDEX_JSON}")
    export_boundary_geojson(input_path=index_wgs, output_path=boundary_geojson)
#endregion

#region Main
def main():
    start_time = datetime.datetime.now() 

    clear_screen()
    get_inputs()
    clear_log()

    try:
        intro_message()
        setup_arcpy()
        process_contour_lines()
        process_boundary_index()
    except Exception as e:
        log(f"An error occurred: {str(e)}")
        raise e
    finally:
        cleanup_arcpy()
        end_time = datetime.datetime.now()
        log_time(start_time, end_time)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)  # Explicit success exit code
    except Exception as e:
        log(f"Error: {e}")
        log(traceback.format_exc())
        sys.exit(1)  # Explicit failure exit code

#endregion