const fs = require('fs')
const { readCSVSync } = require("read-csv-sync")
const { listAvailableDems } = require('./List_Available_DEMs')

const STATE_FOLDER = 'VIRGINIA'
const STATE = 'Virginia'

const log = (message) => {
    console.log(message)
    fs.appendFileSync(`/mnt/z/${STATE_FOLDER}/DEM_COPY.log`, message)
}

const main = async (i, count) => {
    const counties = readCSVSync('../../data/DEM_Allocation/Virginia.csv')

    const county = counties[i]

    const demTiles = []

    for (let project of county.projects.split('|')) {
        const projectTiles = listAvailableDems(STATE, project)
        demTiles.push(...projectTiles)
    }

    log(`(${i}/${count}) Checking ${county.properties.NAME}`)
    const countyTiles = require(`#data/County_UTM_Grids/${county.properties.STATE}/${county.properties.NAME}_${county.properties.LSAD}.json`)

    for (let tile of countyTiles.features) {
        const matches = demTiles.filter(t => t.x === parseInt(tile.properties.Name_X) && t.y === parseInt(tile.properties.Name_Y))

        if (matches.length === 0) {
            const error = `[${county.properties.NAME}] X: ${tile.properties.Name_X}, Y: ${tile.properties.Name_Y} FOUND 0 MATCHES`
            log(error)
        } else if (matches.length > 1) {
            const error = `[${county.properties.NAME}] X: ${tile.properties.Name_X}, Y: ${tile.properties.Name_Y} FOUND ${matches.length} MATCHES`
            log(error)
        }

        const destFolder = `/mnt/z/${STATE_FOLDER}/${county.properties.NAME.replaceAll(' ', '_')}_${county.properties.LSAD.replaceAll(' ', '_')}_Contours/Tif_Files_UTM`

        if (!fs.existsSync(destFolder)) {
            fs.mkdirSync(destFolder, { recursive: true })
        }

        for (let match of matches) {
            const fileNameParts = match.url.split('/')
            const fileName = fileNameParts[fileNameParts.length - 1]
            log(`Copying /mnt/z/${STATE_FOLDER}_NICKs/Tif_Files_UTM/${match.project}/${fileName} -> ${destFolder}/${fileName}`)
            fs.copyFileSync(`/mnt/z/${STATE_FOLDER}_NICKs/Tif_Files_UTM/${match.project}/${fileName}`, `${destFolder}/${fileName}`)
        }
    }
}

if (require.main === module) {
    console.log(main(process.slice(2)))
  }
  
  module.exports = main