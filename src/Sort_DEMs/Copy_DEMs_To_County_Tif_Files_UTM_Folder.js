const counties = require('#data/US_Counties_Detailed.json')
const { listAvailableDems } = require('./List_Available_DEMs')
const fs = require('fs')

const STATE_FOLDER = 'VIRGINIA'

const log = (message) => {
    console.log(message)
    fs.appendFileSync(`/mnt/z/${STATE_FOLDER}/DEM_COPY.log`, message)
}

const main = async (i) => {
    const STATE = 'Virginia'

    const demTiles = await listAvailableDems(`${STATE_FOLDER}`)

    const stateCounties = counties.features.filter(c => c.properties.STATE === STATE)

    // for (let county of stateCounties) {
        const county = stateCounties[i]
        log(`(${i}/134) Checking ${county.properties.NAME}`)
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
    // }
}

main(process.argv[2])