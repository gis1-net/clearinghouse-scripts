import arcpy
 
mosaic_path = r"Z:\VIRGINIA\Alleghany_County_Contours\Contours_Step1.gdb\Mosaic_Dataset_UTM"
 
print(f"Mosaic Dataset Path: {mosaic_path}")
 
# Describe the mosaic dataset
desc = arcpy.Describe(mosaic_path)
 
# Get spatial reference
sr = desc.spatialReference
 
# Print spatial reference info
print(f"Name: {sr.name}")
print(f"Factory Code: {sr.factoryCode}")
print(f"XY Units: {sr.linearUnitName}")
 
# Decide on Z-Factor based on XY units
if sr.linearUnitName.lower() == "meter":
    z_factor = 0.3048
elif "foot" in sr.linearUnitName.lower():
    z_factor = 1.0
else:
    raise ValueError(f"Unknown XY unit: {sr.linearUnitName}")
 
print(f"Z-Factor to apply: {z_factor}")