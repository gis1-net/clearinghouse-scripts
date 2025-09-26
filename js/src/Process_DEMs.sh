# node DEM_Allocation/Allocate_DEM_Files_Multithreaded 64 $1

while : ; do
    node DEM_Download/DEM_Download_Tiles_Multithreaded.js 64 $1
    [[ $? == 0 ]] || break
done

node DEM_Sort/DEM_Sort_Multithreaded.js 64 $1