const fs = require('fs')
const ObjectsToCsv = require('objects-to-csv');

const main = async () => {
    const contourFolders = fs.readdirSync('/mnt/z/VIRGINIA').filter(f => f.endsWith('_Contours'))

    const csvData = []

    for (let contourFolder of contourFolders) {
        const dwgCount = fs.readdirSync(`/mnt/z/VIRGINIA/${contourFolder}/Dwg_Files`).filter(f => f.endsWith('.dwg')).length
        const shpCount = fs.readdirSync(`/mnt/z/VIRGINIA/${contourFolder}/Shapefiles`).filter(f => f.endsWith('.shp')).length

        csvData.push({ contourFolder, dwgCount, shpCount })
    }

    const csv = new ObjectsToCsv(csvData)
    await csv.toDisk(`/mnt/z/Clearinghouse_Support/data/Reports/VIRGINIA_Contours_Report.csv`)

}

main()