const turf = require('@turf/turf')
const fs = require('fs')
const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')

const counties = readJsonData('US_County_Details_And_Boundaries.geojson')
const utmZones = readJsonData('UTM_Zone_Boundaries.geojson')
const utmZoneTiles = []

const main = async (i) => {

  const county = counties.features[i]
  console.log(`(${i}/${counties.features.length}) Checking ${county.properties.NAME} ${county.properties.LSAD}`)
  const tiles = []

  for (let j in utmZones.features) {
    const utmZone = utmZones.features[j]

    const countyGeometry = turf.buffer(turf.feature(county).geometry, .3, { units: "kilometers" })

    if (turf.booleanIntersects(turf.feature(utmZone).geometry, countyGeometry)) {
      utmZoneTiles[utmZone.properties.UTM_ZONE] = readJsonData(`UTM_10k_Index_Grids/${utmZone.properties.UTM_ZONE}.geojson`)

      for (let k in utmZoneTiles[utmZone.properties.UTM_ZONE].features) {
        const tile = utmZoneTiles[utmZone.properties.UTM_ZONE].features[k]
        console.log(`(${i}/${counties.features.length})(${j})(${k}/${utmZoneTiles[utmZone.properties.UTM_ZONE].features.length}) Checking ${county.properties.NAME} ${county.properties.LSAD} tile x:${tile.properties.Name_X} y:${tile.properties.Name_Y}`)

        if (turf.booleanIntersects(turf.feature(tile).geometry, countyGeometry)) {
          tiles.push(tile)
        }
      }
    }
  }

  writeJsonData(`UTM_10k_Index_Grids_By_County/${county.properties.STATE}/${county.properties.NAME}_${county.properties.LSAD}.json`, { type: 'FeatureCollection', features: tiles })
}

main(process.argv[2])
