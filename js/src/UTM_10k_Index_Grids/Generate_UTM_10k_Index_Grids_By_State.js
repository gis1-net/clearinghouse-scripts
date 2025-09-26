const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const turf = require('@turf/turf')
const fs = require('fs')
const { groupBy } = require('lodash')

const counties = readJsonData('US_County_Details_And_Boundaries.geojson')

const main = async (i) => {
  const groupedByState = groupBy(counties.features, c => c.properties.STATE)

  const state = Object.keys(groupedByState)[i]
  const stateGroup = groupedByState[state]

  const groupedByZone = groupBy(stateGroup, c => c.properties.UTM_ZONE)

  for (let zone in groupedByZone) {
    const features = []

    const utmTiles = readJsonData(`UTM_10k_Index_Grids/${zone}.geojson`)

    const area = groupedByZone[zone].length > 1 
      ? turf.union(turf.featureCollection(groupedByZone[zone].map(c => turf.feature(c.geometry))))
      : turf.feature(groupedByZone[zone][0].geometry)
    const areaBuffer = turf.buffer(area, .3, { units: "kilometers" })

    for (let tile of utmTiles.features) {
      console.log(`Checking ${state} UTM Zone ${zone} tile: ${tile.properties.Name_X}, ${tile.properties.Name_Y}`)
      if (turf.booleanIntersects(areaBuffer, tile.geometry)) {
        features.push(tile)
      }
    }

    writeJsonData(`UTM_10k_Index_Grids_By_State/${state}/${state}_UTM_Zone_${zone}_10k_Index_Grid.geojson`, { type: 'FeatureCollection', features })
  }
}

if (require.main === module) {
  main(process.argv[2])
}

module.exports = main