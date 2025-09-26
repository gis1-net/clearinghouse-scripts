# -*- coding: utf-8 -*-
"""
Updated Script to Process Feature Classes and Export Shapefiles
"""
import arcpy
import os
import multiprocessing
import logging
from datetime import datetime

# Define variables at the top for clarity
input_workspace = r"D:\SOUTH_CAROLINA\SavannahPeeDeeArea\Savannah_Pee_Dee_Area_Part5.gdb"
feature_dataset = "Smoothed_PAEK_10FT"
output_folder = r"D:\SOUTH_CAROLINA\shapefiles_Part5"
suffixes = {
    "1Ft": None,
    "2Ft": "Line_Type = 'Index-10' Or Line_Type = 'Intermediate-2'"
}
log_file = r"D:\SOUTH_CAROLINA\logs\part5_log.txt"

# Configure logging
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
logging.getLogger().addHandler(console_handler)

def log_message(message):
    """Log messages to both console and file."""
    print(message)
    logging.info(message)

def feature_class_generator(workspace, wild_card="*", feature_type="ALL", recursive=False):
    """Generator to yield full paths and names of feature classes."""
    with arcpy.EnvManager(workspace=workspace):
        dataset_list = [""]
        if recursive:
            dataset_list.extend(arcpy.ListDatasets())

        for dataset in dataset_list:
            dataset_path = os.path.join(workspace, dataset) if dataset else workspace
            feature_classes = arcpy.ListFeatureClasses(wild_card, feature_type, dataset)
            if feature_classes:
                for fc in feature_classes:
                    # Filter for feature classes that begin with "S"
                    if fc.startswith("S"):
                        yield os.path.join(dataset_path, fc), fc

def process_feature_class(fc_path, fc_name, output_folder, suffixes):
    """Process a single feature class by applying select operations."""
    try:
        # Check if the feature class contains any features
        feature_count = int(arcpy.management.GetCount(fc_path)[0])
        if feature_count == 0:
            log_message(f"Skipping empty feature class: {fc_name}")
            return

        log_message(f"Processing feature class: {fc_name}")

        for suffix, where_clause in suffixes.items():
            output_path = os.path.join(output_folder, f"{fc_name}_{suffix}.shp")
            log_message(f"  -> Exporting {fc_name} with suffix '{suffix}' to {output_path}")
            arcpy.analysis.Select(
                in_features=fc_path,
                out_feature_class=output_path,
                where_clause=where_clause
            )

            # Remove additional unwanted files (.xml and .cpg)
            for ext in [".xml", ".cpg"]:
                unwanted_file = output_path.replace(".shp", ext)
                if os.path.exists(unwanted_file):
                    os.remove(unwanted_file)
                    log_message(f"    -> Deleted {unwanted_file}")

        log_message(f"  -> Completed processing {fc_name}")

    except Exception as e:
        log_message(f"  !! Error processing {fc_name}: {e}")




def process_all_features_parallel(fc_list, output_folder, suffixes):
    """Process all feature classes in parallel using multiprocessing."""
    log_message("Starting parallel processing...")
    tasks = []

    # Prepare arguments for multiprocessing
    for fc_path, fc_name in fc_list:
        args = (fc_path, fc_name, output_folder, suffixes)
        tasks.append(args)

    # Use multiprocessing Pool to process feature classes in parallel
    with multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1) as pool:
        pool.starmap(process_feature_class, tasks)

    log_message("Parallel processing completed.")

def main():
    # Log inputs
    log_message("Script started.")
    log_message(f"Input workspace: {input_workspace}")
    log_message(f"Output folder: {output_folder}")
    log_message(f"Suffixes and where clauses: {suffixes}")

    # Scan the workspace and retrieve feature classes
    log_message(f"Scanning workspace: {input_workspace}")
    fc_list = list(feature_class_generator(os.path.join(input_workspace, feature_dataset)))

    if not fc_list:
        log_message(f"Workspace does not exist or contains no feature classes starting with 'S': {input_workspace}")
        log_message("No feature classes found. Exiting.")
        return

    log_message(f"Found {len(fc_list)} feature classes starting with 'S' to process.")

    # Process feature classes
    process_all_features_parallel(fc_list, output_folder, suffixes)

    log_message("Script completed.")

if __name__ == "__main__":
    main()
