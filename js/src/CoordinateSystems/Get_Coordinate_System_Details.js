const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const projects = readJsonData('Lidar_Project_Boundaries.geojson')

function isInteger(value) {
    return /^-?\d+$/.test(value);
}

const main = async () => {
    const coordinateSystemIds = new Set()

    for (let project of projects.features) {
        if (isInteger(project.properties.horiz_crs)) {
          coordinateSystemIds.add(`${project.properties.horiz_crs}`)
        }
        if (isInteger(project.properties.vert_crs)) {
          coordinateSystemIds.add(`${project.properties.vert_crs}`)
        }
    }

    console.log(coordinateSystemIds)

    const coordinateSystemDetails = []

    for (let csId of Array.from(coordinateSystemIds)) {
        const url = `https://api.maptiler.com/coordinates/search/${csId}.json?key=1CKnQ6XsXsFUCCy01a5R`
        console.log(`FETCHING ${url}`)
        const response = await fetch(url)
        const json = await response.json()
        const csDetails = json.results[0]

        coordinateSystemDetails.push(csDetails)
    }

    writeJsonData('Coordinate_Systems/coordinate_system_details_new.json', coordinateSystemDetails)
}

main()