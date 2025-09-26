import arcpy
import os
import csv
 
def scan_tifs(folder, output_csv):
    results = []
 
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".tif"):
                tif_path = os.path.join(root, file)
                try:
                    desc = arcpy.Describe(tif_path)
                    nodata = None
                    if hasattr(desc, "noDataValue"):
                        nodata = desc.noDataValue
                    elif hasattr(desc, "extent"):  # fallback if no direct property
                        nodata = arcpy.GetRasterProperties_management(tif_path, "NODATA").getOutput(0)
                    results.append([tif_path, nodata])
                except Exception as e:
                    print(f"⚠️ Error processing {tif_path}: {e}")
                    results.append([tif_path, "ERROR"])
 
    # Write results to CSV
    with open(output_csv, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["File", "NoData Value"])
        writer.writerows(results)
 
    print(f"✅ Done! Results saved to {output_csv}")
 
# Example usage:
input_folder = r"Z:\Virginia\York_County_Contours\Tif_Files_UTM"
output_csv = r"Z:\Virginia\York_County_Contours\nodata_report.csv"
scan_tifs(input_folder, output_csv)