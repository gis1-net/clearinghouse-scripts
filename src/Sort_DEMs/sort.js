const counties = require('#data/US_Counties_Detailed.json')
const { listDems } = require('./list_dems')
const fs = require('fs')

const main = async () => {
    const STATE_FOLDER = 'VIRGINIA'
    const STATE = 'Virginia'
    const errors = []

    const demTiles = await listDems(STATE_FOLDER)

    const stateCounties = counties.features.filter(c => c.properties.STATE === STATE)

    for (let county of stateCounties) {
        console.log(`Checking ${county.properties.NAME}`)
        const countyTiles = require(`#data/County_UTM_Grids/${county.properties.STATE}/${county.properties.NAME}.json`)

        for (let tile of countyTiles.features) {
            const matches = demTiles.filter(t => t.x === parseInt(tile.Name_X) && t.y === parseInt(tile.Name_Y))

            if (matches.length === 0) {
                const error = `[${county.properties.NAME}] X: ${tile.Name_X}, Y: ${tile.Name_Y} FOUND 0 MATCHES`
                console.log(error)
                errors.push(error)
            } else if (matches.length > 1) {
                const error = `[${county.properties.NAME}] X: ${tile.Name_X}, Y: ${tile.Name_Y} FOUND ${matches.length} MATCHES`
                console.log(error)
                errors.push(error)
            }

            const destFolder = `/mnt/z/${STATE}/${county.properties.NAME}/Tif_Files_UTM`

            if (!fs.existsSync(destFolder)) {
                fs.mkdirSync(destFolder, { recursive: true })
            }

            for (let match of matches) {
                const fileNameParts = match.url.split('/')
                const fileName = fileNameParts[fileNameParts.length - 1]
                console.log(`Copying /mnt/z/${STATE}/Tif_Files_UTM/${match.project}/${fileName} -> ${destFolder}/${fileName}`)
                fs.copyFileSync(`/mnt/z/${STATE}/Tif_Files_UTM/${match.project}/${fileName}`, `${destFolder}/${fileName}`)
            }

            fs.writeFileSync(`/mnt/z/${STATE}/DEM_COPY.log`, JSON.stringify(errors, null, 2))
        }
    }
}

main()