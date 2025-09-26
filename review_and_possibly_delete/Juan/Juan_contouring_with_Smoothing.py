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

    log_file = os.path.join(log_dir, "contouring.log")
    
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


# Function to check existence, delete, and confirm deletion of ArcGIS objects
def check_and_delete(feature_class_path):
    if arcpy.Exists(feature_class_path):
        log(f"Feature class exists: {feature_class_path}, deleting...")
        
        # Attempt to delete the feature class
        Delete_Succeeded = arcpy.management.Delete(in_data=[feature_class_path])[0]
        
        # Confirm deletion
        if not arcpy.Exists(feature_class_path):
            log(f"Successfully deleted: {feature_class_path}")
        else:
            log(f"Deletion failed: {feature_class_path}")
    else:
        log(f"Feature class does not exist: {feature_class_path}")




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
    log_file = os.path.join(log_dir, "contouring.log")
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
    output_feature_dataset = os.path.join(base_path, f"{county_name}_Contours.gdb", "Smoothed_PAEK_10FT")
    index_5000_feature_class = os.path.join(base_path, f"{county_name}_Contours.gdb", "Index_5000Ft")
    contour_lines_sp_feature_class = os.path.join(base_path, "Contours_Step2.gdb", "Contours_SP", "Contour_Lines_SP")
    contour_lines_sp_wrong = os.path.join(base_path, "Contours_Step2.gdb", "Contour_Lines_SP") # Contour_Lines_SP at the root of Contours_Step2 - WRONG location
    smoothed_contour_lines_feature_class = os.path.join(base_path, "Contours_Step3.gdb", "Smoothed_Contours", "Smoothed_Contour_Lines")
    shapefile_output_folder = os.path.join(base_path, "Shapefiles")
    dwg_output_folder = os.path.join(base_path, "DWG_files")
    contour_gdb = os.path.join(base_path, f"{county_name}_Contours.gdb")
    step1_gdb = os.path.join(base_path, "Contours_Step1.gdb")
    output_geojson = os.path.join(base_path, f"{county_name}_Contours_Index.geojson")
    boundary_utm = os.path.join(contour_gdb, "Mosaic_Boundary_UTM" if elevation_meters else "Mosaic_Boundary_SP")
    
    # Ensure the output shapefile folder exists
    if not os.path.exists(shapefile_output_folder):
        os.makedirs(shapefile_output_folder)
        
    # Ensure the output DWG_files folder exists
    if not os.path.exists(dwg_output_folder):
        os.makedirs(dwg_output_folder)
    
    # Ensure there is no Contours_Line_SP created from an old model
    check_and_delete(contour_lines_sp_feature_class)
    check_and_delete(contour_lines_sp_wrong)
    
    # Ensure there is no Boundary_UTM from an old model
    check_and_delete(boundary_utm)
    
    # Log initial variables
    log("Initial variables:")
    log(f"  input_mosaic_dataset: {input_mosaic_dataset}")
    log(f"  output_feature_dataset: {output_feature_dataset}")
    log(f"  index_5000_feature_class: {index_5000_feature_class}")
    log(f"  contour_lines_sp_feature_class: {contour_lines_sp_feature_class}")
    log(f"  smoothed_contour_lines_feature_class: {smoothed_contour_lines_feature_class}")
    log(f"  shapefile_output_folder: {shapefile_output_folder}")
    log(f"  dwg_output_folder: {dwg_output_folder}")
    log(f"  contour_gdb: {contour_gdb}")
    log(f"  step1_gdb: {step1_gdb}")
    log(f"  output_geojson: {output_geojson}")
    log(f"  boundary_utm: {boundary_utm}")


    # Confirm to proceed if not skipping confirmation
    if not skip_confirmation:
        proceed = input("Do you want to proceed with the script? (y/n): ").strip().lower()
        if proceed != 'y':
            log("Script execution cancelled by user.")
            return

    try:
        # Set environment settings
        arcpy.env.overwriteOutput = True
        
        # Setting this to ZERO so LocalWorker.exe doesn't go crazy      
        arcpy.env.parallelProcessingFactor = "0"

        
        log("Environment overwriteOutput set to True.")

        # Check out necessary licenses
        arcpy.CheckOutExtension("3D")
        arcpy.CheckOutExtension("spatial")
        log("Checked out 3D and Spatial Analyst extensions.")
        
        # Added 2/27/25 due to some counties failing with ERROR 010667: The statistics of the raster are not up to date
        #
        # Calculate statistics for the raster (before running Contour)
        log("Calculating raster statistics...")
        arcpy.management.CalculateStatistics(input_mosaic_dataset)
        log("Raster statistics calculated.")
                
        #
        # End of 2/27/25 Add

        # Setting this back to normal
        arcpy.env.parallelProcessingFactor = None



        # Contour process
        log("Starting Contour process.")
        utm_contours_elev_ft = os.path.join(os.path.dirname(input_mosaic_dataset), "UTM_Contours_Elev_Ft")
        arcpy.ddd.Contour(
            in_raster=input_mosaic_dataset,
            out_polyline_features=utm_contours_elev_ft,
            contour_interval=1,
            z_factor=z_factor,
            max_vertices_per_feature=500000
        )
        log(f"Contour process completed. Output: {utm_contours_elev_ft}")

        # Make Feature Layer
        log("Creating feature layer from contours.")
        contour_lines_layer = "UTM_Contours_Elev_Ft_Layer"
        arcpy.management.MakeFeatureLayer(
            in_features=utm_contours_elev_ft, 
            out_layer=contour_lines_layer
        )
        log("Feature layer created.")

        # Select Layer By Attribute
        min_length = (5 * 3.280839895) / z_factor

        log(f"Selecting features with Shape_Length < {min_length}.")
        selected_layer, count = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=contour_lines_layer, 
            where_clause=f"Shape_Length < {min_length}"
        )
        log(f"Selected {count} features.")

        # Delete Features
        log("Deleting selected features.")
        arcpy.management.DeleteFeatures(selected_layer)
        log("Selected features deleted.")

        # Project
        log("Projecting contour lines.")
        arcpy.management.Project(
            in_dataset=selected_layer,
            out_dataset=contour_lines_sp_feature_class,
            # NOTE: out_coor_system is not used because out_dataset is a FeatureDataSet that has a pre-defined coordinate system that overrides any input
            # However, the function requires a valid coordinate system be provided as an argument
            out_coor_system="PROJCS[\"NAD_1983_2011_StatePlane_South_Carolina_FIPS_3900_Ft_Intl\",GEOGCS[\"GCS_NAD_1983_2011\",DATUM[\"D_NAD_1983_2011\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Lambert_Conformal_Conic\"],PARAMETER[\"False_Easting\",2000000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-81.0],PARAMETER[\"Standard_Parallel_1\",32.5],PARAMETER[\"Standard_Parallel_2\",34.83333333333334],PARAMETER[\"Latitude_Of_Origin\",31.83333333333333],UNIT[\"Foot\",0.3048]]"
        )
        log(f"Projection completed. Output: {contour_lines_sp_feature_class}")


        # Smooth Line
        log("Smoothing contour lines.")
        arcpy.cartography.SmoothLine(
            in_features=contour_lines_sp_feature_class,
            out_feature_class=smoothed_contour_lines_feature_class,
            algorithm="PAEK",
            tolerance="10 Feet",
            error_option="RESOLVE_ERRORS" 
        )
        log(f"Smooth Line process completed. Output: {smoothed_contour_lines_feature_class}")


        # ****************** New Step added 1/6/2025
        # Process: Select Layer By Location (Select Layer By Location) (management)
        # Avoids trying to create a tile for areas with no contour lines.
        #log("Eliminating areas with no contour lines")
        #if county_name and state_name:
        #    index_5000_feature_class, Output_Layer_Names, Count = arcpy.management.SelectLayerByLocation(
        #    in_layer=[index_5000_feature_class], 
        #    select_features=smoothed_contour_lines_feature_class, 
        #    invert_spatial_relationship="INVERT"
        #)
        # Process: Delete Features (Delete Features) (management)
        #if county_name and state_name:
        #    Output_Feature_Class = arcpy.management.DeleteFeatures(in_features=index_5000_feature_class)[0]
        # *****************End of New Step added 1/6/2025


        # Add Field and Calculate Field
        log("Adding and calculating Elevation field.")
        arcpy.management.AddField(
            in_table=smoothed_contour_lines_feature_class,
            field_name="Elevation",
            field_type="LONG"
        )
        arcpy.management.CalculateField(
            in_table=smoothed_contour_lines_feature_class,
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
            in_table=smoothed_contour_lines_feature_class,
            field_name="Line_Type",
            field_type="TEXT",
            field_length=20
        )

        arcpy.management.CalculateField(
            in_table=smoothed_contour_lines_feature_class,
            field="Line_Type",
            expression="reclass(!Elevation!)",
            expression_type="PYTHON3",
            code_block=reclass_code
        )

        log("Line_Type field reclassified.")


        # Delete Unnecessary Fields
        log("Deleting unnecessary fields.")
        arcpy.management.DeleteField(
            in_table=smoothed_contour_lines_feature_class, 
            drop_field=["Id", "Contour", "InLine_FID"]
        )
        log("Fields deleted.")

        # Split
        log("Splitting smoothed contour lines.")
        arcpy.analysis.Split(
            in_features=smoothed_contour_lines_feature_class,
            split_features=index_5000_feature_class,
            split_field="TILE_NUM",
            out_workspace=output_feature_dataset
        )
        log(f"Split process completed. Output workspace: {output_feature_dataset}")
        
        # Added 2/27/25 Database compaction
        
        # Intermediate compaction of the county contours geodatabase
        # (This geodatabase is reused later for exporting and further processing)
        county_contours_gdb = os.path.join(base_path, f"{county_name}_Contours.gdb")
        log(f"Compacting geodatabase: {county_contours_gdb}")
        arcpy.Compact_management(county_contours_gdb)
        log("Intermediate geodatabase compaction completed.")
        
        # End Add 2/27/25
        
        
        # Export to shapefiles 1Ft and 2Ft, and DWG CAD files
        # Iterate through all line feature classes in the specified dataset
        log("Iterating through all line feature classes in the specified dataset.")
        for FC_Variable, Name in FeatureClassGenerator(output_feature_dataset, "", "LINE", "NOT_RECURSIVE"):

            _Name_1Ft_shp = os.path.join(shapefile_output_folder, f"{Name}_1Ft.shp")
            # Process: Multipart To Singlepart
            log("Modifying Multipart to Singlepart shapefiles")
            arcpy.management.MultipartToSinglepart(in_features=FC_Variable, out_feature_class=_Name_1Ft_shp)
            
            log(f"Exporting shapefile:  {_Name_1Ft_shp}")
			
            # Process: Delete Field to delete additional field added by previous step
            log("Deleting added ORIG_FID field from previous step")
            _Name_1Ft_shp_temp = arcpy.management.DeleteField(in_table=_Name_1Ft_shp, drop_field=["ORIG_FID"])[0]
			
            # Recalculate the shape length for the 1Ft in US Survey Feet
            log("Recalculating Geometry of the shape length in US Survey feet for the 1Ft")
            arcpy.management.CalculateGeometryAttributes(
                _Name_1Ft_shp_temp,
                [["Shape_Leng", "LENGTH"]],
                length_unit="FEET_US"
            )
            
            
			

			
						
            # Export DWG 1Ft
            # Use the feature class name as the prefix for the exported DWG
            _Name_1Ft_dwg = os.path.join(dwg_output_folder, f"{Name}_1Ft.dwg")
            log(f"Exporting DWG:        {_Name_1Ft_dwg}")
            # Process: Export Features
            arcpy.conversion.ExportCAD(
                in_features=_Name_1Ft_shp_temp,
                Output_Type="DWG_R2018",
                Output_File=_Name_1Ft_dwg
                )
				
			
            # Process: Make Feature Layer (Make Feature Layer) (management)
            Output_Layer = f"{Name}_1Ft_Layer"
            arcpy.management.MakeFeatureLayer(in_features=_Name_1Ft_shp_temp, out_layer=Output_Layer)
			
            # Process: Select (Select) (analysis)
            # Use the feature class name as the prefix for the exported shapefile
            _Name_2Ft_shp = os.path.join(shapefile_output_folder, f"{Name}_2Ft.shp")
			
            log(f"Exporting shapefile:  {_Name_2Ft_shp}")
            arcpy.analysis.Select(in_features=Output_Layer, out_feature_class=_Name_2Ft_shp, where_clause="Line_Type = 'Index-10' Or Line_Type = 'Intermediate-2'")
            
            #log("Recalculating Geometry of the shape length in US Survey feet for the 2Ft")
            # Recalculate the shape length for the 2Ft in US Survey Feet
            #arcpy.management.CalculateGeometryAttributes(
            #    _Name_2Ft_shp,
            #    [["Shape_Leng", "LENGTH"]],
            #    length_unit="FEET_US"
            #)
			
            
            # Export DWG 2Ft
            # Use the feature class name as the prefix for the exported DWG
            _Name_2Ft_dwg = os.path.join(dwg_output_folder, f"{Name}_2Ft.dwg")
            log(f"Exporting DWG:        {_Name_2Ft_dwg}")
            # Process: Export Features
            arcpy.conversion.ExportCAD(
                in_features=_Name_2Ft_shp,
                Output_Type="DWG_R2018",
                Output_File=_Name_2Ft_dwg
                )
            
              
            
        log("Cleaning up auxiliary files in the shapefile output folder: .shp.xml, .sbx, .sbn, .cpg.")
        aux_extensions = [".shp.xml", ".sbx", ".sbn", ".cpg"]
        deleted_files = 0
 
        for root, _, files in os.walk(shapefile_output_folder):
            for file in files:
                # Check if the file has one of the auxiliary extensions
                if any(file.endswith(ext) for ext in aux_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        log(f"Deleted auxiliary file: {file_path}")
                        deleted_files += 1
                    except Exception as e:
                        log(f"Failed to delete {file_path}: {e}")
 
        log(f"Cleanup completed. Total auxiliary Shapefiles deleted: {deleted_files}.")
        
        
        log("Cleaning up auxiliary files in the DWG output folder: .dww.xml")
        aux_extensions = [".dwg.xml"]
        deleted_files = 0
 
        for root, _, files in os.walk(dwg_output_folder):
            for file in files:
                # Check if the file has one of the auxiliary extensions
                if any(file.endswith(ext) for ext in aux_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        log(f"Deleted auxiliary file: {file_path}")
                        deleted_files += 1
                    except Exception as e:
                        log(f"Failed to delete {file_path}: {e}")
 
        log(f"Cleanup completed. Total auxiliary DWG files deleted: {deleted_files}.")

        # End of Export to shapefiles

    
        # Start of Create Data Boundary Index for Clearinghouse  - Added 2/2/2025
        
        # ***** Chad requested to disable this 6/19/25  ************
        # Process 1: Define Mosaic Dataset NoData
        #log("Defining mosaic dataset NoData values")
        #md_nodata = arcpy.management.DefineMosaicDatasetNoData(
        #    input_mosaic_dataset, 
        #    num_bands=1, 
        #    bands_for_nodata_value=[["ALL_BANDS", "0"]]
        #)[0]
        
        # **********************************************************

        # Process 2: Build Footprints
        log("Building mosaic dataset footprints")
        md_footprints = arcpy.management.BuildFootprints(
            md_nodata,
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


        # Process 3: Export Mosaic Boundary (FIXED)
        log("Exporting mosaic boundary geometry")
                                   
        arcpy.management.ExportMosaicDatasetGeometry(md_footprints, boundary_utm)


        # Process 4: Project to State Plane
        log("Projecting to Mississippi East State Plane")
        boundary_sp = os.path.join(contour_gdb, "Smoothed_PAEK_10FT", "Mosaic_Boundary_SP")
        # sr = arcpy.SpatialReference(6557) # WKID for NAD83(2011) / South Carolina (ft)" coordinate system
        sr = arcpy.SpatialReference(6507)   # WKID_for_Mississippi_East_StatePlane
        # That WKID for MS is the same as as using "PROJCS[\"NAD_1983_2011_StatePlane_Mississippi_East_FIPS_2301_Ft_US\",GEOGCS[\"GCS_NAD_1983_2011\",DATUM[\"D_NAD_1983_2011\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",984250.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-88.83333333333333],PARAMETER[\"Scale_Factor\",0.99995],PARAMETER[\"Latitude_Of_Origin\",29.5],UNIT[\"Foot_US\",0.3048006096012192]]")
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
        

        # End of of Create Data Boundary Index for Clearinghouse

   

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
