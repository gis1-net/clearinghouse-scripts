const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')

const LAT_MAX = 71.5
const LAT_MIN = 17.5

const LONG_MAX = -60
const LONG_MIN = -180

const main = async (project, i = 0, count = 1) => {
//  console.log(`(${i + 1}/${count}) Verifying grid for ${project}...`)

  const grid = readJsonData(`Lidar_Project_Grids/${project}.geojson`)

  if (!grid?.features?.[0]?.geometry?.coordinates?.[0]?.[0]?.[0]) {
    console.log(`Project ${project} has invalid geometry`)
    return false
  }

  const long = grid.features[0].geometry.coordinates[0][0][0]
  const lat = grid.features[0].geometry.coordinates[0][0][1]

  if (long > LONG_MAX || long < LONG_MIN || lat > LAT_MAX || lat < LAT_MIN) {
    console.log(`Project ${project} has invalid coordinates`)
    return false
  }

  return true
}

if (require.main === module) {
  main(...process.argv.slice(2))
}

module.exports = main
