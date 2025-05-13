const fs = require('fs')
const { readCSVSync } = require("read-csv-sync")
const { listAvailableDems } = require('./List_Available_DEMs')
const { readJsonData } = require('#src/Utils/JSON_Data.js')
const countyBoundaries = readJsonData('US_County_Details_And_Boundaries.geojson')
const turf = require('@turf/turf')

let STATE_FOLDER = ''

const log = (message) => {
    console.log(message)
    fs.appendFileSync(`/mnt/z/${STATE_FOLDER}/DEM_COPY.log`, message)
}

const main = (state, i, count) => {
    STATE_FOLDER = state.toUpperCase()
    const counties = readCSVSync(`../../data/DEM_Allocation/${state}.csv`)

    const county = counties[i]
    const countyBoundary = countyBoundaries.features.find(c => c.properties.NAME === county.name && c.properties.LSAD === county.lsad && c.properties.STATE === county.state)
    const countyBoundaryBuffer = turf.buffer(countyBoundary.geometry, 0.3, { units: 'kilometers' })

    const destFolder = `/mnt/z/${STATE_FOLDER}/${county.name.replaceAll(' ', '_')}${county.groupNumber > 1 ? county.groupNumber : ''}_${county.lsad.replaceAll(' ', '_')}_Contours`

    if (!fs.existsSync(destFolder)) {
        fs.cpSync(`/mnt/z/${STATE_FOLDER}/${county.name.replaceAll(' ', '_')}_${county.lsad.replaceAll(' ', '_')}_Contours`, destFolder, { recursive: true })
        fs.rename(`${destFolder}/${county.name.replaceAll(' ', '_')}_${county.lsad.replaceAll(' ', '_')}_Contours.gdb`, `${destFolder}/${county.name.replaceAll(' ', '_')}${county.groupNumber > 1 ? county.groupNumber : ''}_${county.lsad.replaceAll(' ', '_')}_Contours.gdb`, (error) => { if (error) { console.log(error); throw error; } })
    }

    if (!fs.existsSync(`${destFolder}/Tif_Files_UTM`)) {
        fs.mkdir(`${destFolder}/Tif_Files_UTM`, { recursive: false }, (error) => { if (error) { console.log(error); throw error; } })
    }

    for (let project of county.projects.split('|')) {
        console.log(`Checking project ${project}.`)
        const tileGrid = readJsonData(`Lidar_Project_Grids/${project}.geojson`)

        for (let tile of tileGrid.features) {
            console.log(`Checking Tile ${tile.properties.TILE_NAME}.`)
            if (turf.booleanIntersects(tile.geometry, countyBoundaryBuffer.geometry)) {
                if (fs.existsSync(`/mnt/z/${STATE_FOLDER}/Tif_Files_UTM/${project}/${tile.properties.TILE_NAME}.tif`)) {
                    if (!fs.existsSync(`${destFolder}/Tif_Files_UTM/${tile.properties.TILE_NAME}.tif`)) {
                        log(`Copying /mnt/z/${STATE_FOLDER}/Tif_Files_UTM/${project}/${tile.properties.TILE_NAME}.tif -> ${destFolder}/Tif_Files_UTM/${tile.properties.TILE_NAME}.tif`)
                        fs.copyFileSync(`/mnt/z/${STATE_FOLDER}/Tif_Files_UTM/${project}/${tile.properties.TILE_NAME}.tif`, `${destFolder}/Tif_Files_UTM/${tile.properties.TILE_NAME}.tif`)
                    } else {
                        console.log(`Already copied ${destFolder}/Tif_Files_UTM/${tile.properties.TILE_NAME}.tif. Skipping.`)
                    }
                } else {
                    log(`No file found for /mnt/z/${STATE_FOLDER}/Tif_Files_UTM/${project}/${tile.properties.TILE_NAME}.tif`)
                }
            } else {
                console.log(`Tile does not intersect with county.`)
            }
        }
    }
}

if (require.main === module) {
    console.log(main(...process.argv.slice(2)))
}

module.exports = main
