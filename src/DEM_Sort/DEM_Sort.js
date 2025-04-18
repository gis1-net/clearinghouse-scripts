const { readJsonData } = require('src/Utils/JSON_Data')
const { listAvailableDems } = require('./List_Available_DEMs')
const fs = require('fs')

const main = async (i, state) => {
    const stateFolder = state.toUpperCase()

    const log = (message) => {
        console.log(message)
        fs.appendFileSync(`/mnt/z/${stateFolder}/DEM_COPY.log`, message)
    }

    const stateCountyProjects = readJsonData(`DEM_Allocation/${state}.json`)

    const county = stateCountyProjects[i]
    log(`(${i}/${stateCountyProjects.length}) Checking ${county.name}`)

    const demTiles = await listAvailableDems(county.projects_1.split('|'))
    const countyTiles = require(`#data/County_UTM_Grids/${county.state}/${county.name}_${county.lsad}.json`)

    for (let tile of countyTiles.features) {
        const matches = demTiles.filter(t => t.x === parseInt(tile.properties.Name_X) && t.y === parseInt(tile.properties.Name_Y))

        if (matches.length === 0) {
            const error = `[${county.name}] X: ${tile.properties.Name_X}, Y: ${tile.properties.Name_Y} FOUND 0 MATCHES`
            log(error)
        } else if (matches.length > 1) {
            const error = `[${county.name}] X: ${tile.properties.Name_X}, Y: ${tile.properties.Name_Y} FOUND ${matches.length} MATCHES`
            log(error)
        }

        const destFolder = `/mnt/z/${stateFolder}/${county.name.replaceAll(' ', '_')}_${county.lsad.replaceAll(' ', '_')}_Contours/Tif_Files_UTM`

        if (!fs.existsSync(destFolder)) {
            fs.mkdirSync(destFolder, { recursive: true })
        }

        for (let match of matches) {
            const fileNameParts = match.url.split('/')
            const fileName = fileNameParts[fileNameParts.length - 1]
            log(`Copying /mnt/z/${stateFolder}_NICKs/Tif_Files_UTM/${match.project}/${fileName} -> ${destFolder}/${fileName}`)
            fs.copyFileSync(`/mnt/z/${stateFolder}_NICKs/Tif_Files_UTM/${match.project}/${fileName}`, `${destFolder}/${fileName}`)
        }
    }

    return true
}

if (require.main === module) {
  console.log(main(...process.argv.slice(2)))
}

module.exports = main