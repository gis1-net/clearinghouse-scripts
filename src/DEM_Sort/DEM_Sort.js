const fs = require('fs')
const { readCSVSync } = require("read-csv-sync")
const { listAvailableDems } = require('./List_Available_DEMs')
const { readJsonData } = require('#src/Utils/JSON_Data')
const countyBoundaries = readJsonData('US_County_Details_And_Boundaries.geojson')
const turf = require('@turf/turf')

const STATE_FOLDER = ''

const log = (message) => {
    console.log(message)
    fs.appendFileSync(`/mnt/z/${STATE_FOLDER}/DEM_COPY.log`, message)
}

const main = async (state, i, count) => {
    STATE_FOLDER = state.toUpperCase()
    const counties = readCSVSync(`../../data/DEM_Allocation/${state}.csv`)

    const county = counties[i]
    const countyBoundary = countyBoundaries.find(c => c.properties.NAME === county.NAME && c.properties.LSAD === county.LSAD && c.properties.STATE === county.STATE)
    const countyBoundaryBuffer = turf.buffer(countyBoundary.geometry, 0.3, { units: 'kilometers' })

    for (let project of county.projects.split('|')) {
        const tileGrid = readJsonData(`Lidar_Project_Grids/${project}.geojson`)

        for (let tile of tileGrid.features) {
            if (turf.booleanIntersects(tile.geometry, countyBoundaryBuffer.geometry)) {
                if (fs.existsSync(`/mnt/z/${STATE_FOLDER}_NICKs/Tif_Files_UTM/${project}/${tile.TILE_NAME}`)) {
                    log(`Copying /mnt/z/${STATE_FOLDER}_NICKs/Tif_Files_UTM/${project}/${tile.TILE_NAME} -> ${destFolder}/${tile.TILE_NAME}`)
                    fs.copyFileSync(`/mnt/z/${STATE_FOLDER}_NICKs/Tif_Files_UTM/${project}/${tile.TILE_NAME}`, `${destFolder}/${tile.TILE_NAME}`)
                } else {
                    log(`No file found for /mnt/z/${STATE_FOLDER}_NICKs/Tif_Files_UTM/${project}/${tile.TILE_NAME}`)
                }
            }
        }
    }
}

if (require.main === module) {
    console.log(main(process.slice(2)))
  }
  
  module.exports = main