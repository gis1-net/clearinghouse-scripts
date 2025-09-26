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
    
    log_dir = f"Z:\\{state_name}\\{county_name}_County_Contours"

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
    if len(sys.argv) >= 3:
        state_name = sys.argv[1].strip()
        county_name = sys.argv[2].strip()
        skip_confirmation = True  # Skip confirmation if parameters are passed
    else:
        state_name = input("Enter the State Name: ").strip()
        county_name = input("Enter the County Name: ").strip()
        skip_confirmation = False  # Require confirmation if no parameters are passed


    # Clear the log file at the start 
    log_dir = f"Z:\\{state_name}\\{county_name}_County_Contours"
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
    base_path = f"Z:\\{state_name}\\{county_name}_County_Contours"
    input_mosaic_dataset = os.path.join(base_path, "Contours_Step1.gdb", "Mosaic_Dataset_UTM")
    output_feature_dataset = os.path.join(base_path, f"{county_name}_County_Contours.gdb", "Smoothed_PAEK_10FT")
    index_5000_feature_class = os.path.join(base_path, f"{county_name}_County_Contours.gdb", "Index_5000Ft")
    contour_lines_sp_feature_class = os.path.join(base_path, "Contours_Step2.gdb", "Contours_SP", "Contour_Lines_SP")
    contour_lines_sp_wrong = os.path.join(base_path, "Contours_Step2.gdb", "Contour_Lines_SP") # Contour_Lines_SP at the root of Contours_Step2 - WRONG location
    smoothed_contour_lines_feature_class = os.path.join(base_path, "Contours_Step3.gdb", "Smoothed_Contours", "Smoothed_Contour_Lines")
    shapefile_output_folder = os.path.join(base_path, "Shapefiles")
    dwg_output_folder = os.path.join(base_path, "DWG_files")
    contour_gdb = os.path.join(base_path, f"{county_name}_County_Contours.gdb")
    step1_gdb = os.path.join(base_path, "Contours_Step1.gdb")
    output_geojson = os.path.join(base_path, f"{county_name}_County_Contours_Index.geojson")
    boundary_utm = os.path.join(contour_gdb, "Mosaic_Boundary_UTM")
    
    # Ensure the output shapefile folder exists
    if not os.path.exists(shapefile_output_folder):
        os.makedirs(shapefile_output_folder)
        
    # Ensure the output DWG_files folder exists
    if not os.path.exists(dwg_output_folder):
        os.makedirs(dwg_output_folder)
    

    
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
        # log("Calculating raster statistics...")
        # arcpy.management.CalculateStatistics(input_mosaic_dataset)
        # log("Raster statistics calculated.")
                
        #
        # End of 2/27/25 Add

        # Setting this back to normal
        arcpy.env.parallelProcessingFactor = None





    
        # Start of Create Data Boundary Index for Clearinghouse  - Added 2/2/2025
        
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
