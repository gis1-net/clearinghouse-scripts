const fs = require('fs')
const { readCSVSync } = require("read-csv-sync")
const { listAvailableDems } = require('./List_Available_DEMs')
const { readJsonData } = require('#src/Utils/JSON_Data.js')
const countyBoundaries = readJsonData('US_County_Details_And_Boundaries.geojson')
const turf = require('@turf/turf')
const XXH = require('xxhashjs');

let STATE_FOLDER = ''

const log = (message) => {
    console.log(message)
    fs.appendFileSync(`/mnt/z/${STATE_FOLDER}/DEM_COPY.log`, message)
}

async function compareFiles(a, b) {
    const kReadSize = 1024 * 8;
    let h1, h2;

    if (!fs.existsSync(a) || !fs.existsSync(b)) {
        return false
    }

    try {
        h1 = await fs.promises.open(a);
        h2 = await fs.promises.open(b);
        const [stat1, stat2] = await Promise.all([h1.stat(), h2.stat()]);
        if (stat1.size !== stat2.size) {
            return false;
        }
        const buf1 = Buffer.alloc(kReadSize);
        const buf2 = Buffer.alloc(kReadSize);
        let pos = 0;
        let remainingSize = stat1.size;
        while (remainingSize > 0) {
            let readSize = Math.min(kReadSize, remainingSize);
            let [r1, r2] = await Promise.all([h1.read(buf1, 0, readSize, pos), h2.read(buf2, 0, readSize, pos)]);
            if (r1.bytesRead !== readSize || r2.bytesRead !== readSize) {
                throw new Error("Failed to read desired number of bytes");
            }
            if (buf1.compare(buf2, 0, readSize, 0, readSize) !== 0) {
                return false;
            }
            remainingSize -= readSize;
            pos += readSize;
        }
        return true;
    } finally {
        if (h1) {
            await h1.close();
        }
        if (h2) {
            await h2.close();
        }
    }
}


const main = async (state, county) => {
    STATE_FOLDER = state.toUpperCase()
    const counties = readCSVSync(`${__dirname}/../../data/DEM_Allocation/${state}.csv`)

    const countyData = counties.find(c => c.name == county.replaceAll('_', ' '))
    const countyName = countyData.groupNumber > 1 ? countyData.name.replaceAll(/[0-9]/g, '') : countyData.name

    const countyBoundary = countyBoundaries.features.find(c => c.properties.NAME === countyName && c.properties.LSAD === countyData.lsad && c.properties.STATE === countyData.state)
    const countyBoundaryBuffer = turf.buffer(countyBoundary.geometry, 0.3, { units: 'kilometers' })

    const destFolder = `/mnt/z/${STATE_FOLDER}/${countyName.replaceAll(' ', '_')}${countyData.groupNumber > 1 ? countyData.groupNumber : ''}_${countyData.lsad.replaceAll(' ', '_')}_Contours`

    if (!fs.existsSync(destFolder)) {
        fs.mkdirSync(destFolder)

        const items = fs.readdirSync(`/mnt/z/${STATE_FOLDER}/${countyName.replaceAll(' ', '_')}_${countyData.lsad.replaceAll(' ', '_')}_Contours`)

        for (let item of items) {
            if (item != 'Tif_Files_UTM') {
              fs.cpSync(`/mnt/z/${STATE_FOLDER}/${countyName.replaceAll(' ', '_')}_${countyData.lsad.replaceAll(' ', '_')}_Contours/${item}`, `${destFolder}/${item}`, { recursive: true })
            }
        }
        fs.rename(`${destFolder}/${countyName.replaceAll(' ', '_')}_${countyData.lsad.replaceAll(' ', '_')}_Contours.gdb`, `${destFolder}/${countyName.replaceAll(' ', '_')}${countyData.groupNumber > 1 ? countyData.groupNumber : ''}_${countyData.lsad.replaceAll(' ', '_')}_Contours.gdb`, (error) => { if (error) { console.log(error); throw error; } })
    }

    if (!fs.existsSync(`${destFolder}/Tif_Files_UTM`)) {
        fs.mkdir(`${destFolder}/Tif_Files_UTM`, { recursive: false }, (error) => { if (error) { console.log(error); throw error; } })
    }

    for (let project of countyData.projects.split('|')) {
        console.log(`Checking project ${project}.`)
        const tileGrid = readJsonData(`Lidar_Project_Grids/${project}.geojson`)

        for (let tile of tileGrid.features) {
            console.log(`Checking Tile ${tile.properties.TILE_NAME}.`)
            if (turf.booleanIntersects(tile.geometry, countyBoundaryBuffer.geometry)) {
                console.log(`Tile intersects with county`)
                const srcFile = `/mnt/z/${STATE_FOLDER}/Tif_Files_UTM/${project}/${tile.properties.TILE_NAME}.tif`
                const destFile = `${destFolder}/Tif_Files_UTM/${tile.properties.TILE_NAME}.tif`

                if (fs.existsSync(`${srcFile}`)) {
                    console.log('Comparing files...')
                    let filesMatch = await compareFiles(srcFile, destFile)

                    while (!filesMatch) {
                        log(`Copying ${srcFile} -> ${destFile}`)
                        fs.copyFileSync(srcFile, destFile)

                        console.log('Comparing files...')
                        filesMatch = await compareFiles(srcFile, destFile)

                        if (!filesMatch) {
                            console.log(`File comparison ${destFile} failed, retrying.`)
                        }
                    }
                } else {
                    log(`No file found for ${srcFile}`)
                }
            } else {
                console.log(`Tile does not intersect with county.`)
            }
        }
    }
}

if (require.main === module) {
    main(...process.argv.slice(2))
}

module.exports = main
