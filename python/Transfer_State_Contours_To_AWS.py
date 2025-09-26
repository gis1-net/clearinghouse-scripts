import os
import concurrent.futures
import subprocess

def upload_county_data(source_folder, state):
    """Handle all upload tasks for a single county"""
    folder_name = os.path.basename(source_folder)
    county_name = folder_name.lower().replace('_county_contours', '')
    dest_base = f"data/Contour_Lines/{state.lower()}/{county_name}/GIS1"
    
    try:
        # Upload index file
        index_src = os.path.join(source_folder, f"{folder_name}_Index.geojson")
        subprocess.run([
            'aws', 's3', 'cp', 
            index_src,
            f's3://storage.data.gis1.net/{dest_base}/index.json'
        ], check=True)
        
        # Upload Dwg_Files
        dwg_src = os.path.join(source_folder, 'Dwg_Files')
        subprocess.run([
            'aws', 's3', 'sync',
            dwg_src,
            f's3://storage.data.gis1.net/{dest_base}'
        ], check=True)
        
        # Upload Shapefiles
        shp_src = os.path.join(source_folder, 'Shapefiles')
        subprocess.run([
            'aws', 's3', 'sync',
            shp_src,
            f's3://storage.data.gis1.net/{dest_base}'
        ], check=True)
        
        return f"Success: {folder_name}"
    except subprocess.CalledProcessError as e:
        return f"Error in {folder_name}: {str(e)}"

def main():
    state = input("Enter the name of the state folder (e.g. SOUTH_CAROLINA): ")
    concurrency = int(input("Enter number of concurrent uploads (10-20 recommended): "))
    
    base_dir = f"W:\\{state}"
    counties = [
        f.path for f in os.scandir(base_dir) 
        if f.is_dir()
        and '_County_Contours' in f.name
        and 'Empty' not in f.name
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(upload_county_data, county, state): county for county in counties}
        
        for future in concurrent.futures.as_completed(futures):
            county_path = futures[future]
            county_name = os.path.basename(county_path)
            try:
                result = future.result()
                print(f"Completed: {county_name} - {result}")
            except Exception as e:
                print(f"Exception in {county_name}: {str(e)}")

if __name__ == '__main__':
    main()