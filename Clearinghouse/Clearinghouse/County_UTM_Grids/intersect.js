const counties = require('../Counties/US_Counties_Detailed.json')
const turf = require('@turf/turf')
const utmZones = require('../UTM_Grids/UTM_Zones.json')
const fs = require('fs')
const utmZoneTiles = []

for (let i = 1; i <= 19; i++) {
  utmZoneTiles[i] = require(`../UTM_Grids/UTM_Grids/${i}.json`)
}

const main = async () => {
  const i = process.argv[2]

  // for (let i in counties.features) {
    const county = counties.features[i]
    console.log(`(${i}/${counties.features.length}) Checking ${county.properties.NAME}`)
    const tiles = []

    for (let j in utmZones.features) {
      const utmZone = utmZones.features[j]
      console.log(turf.feature(utmZone), turf.feature(county).geometry)

      if (turf.booleanIntersects(turf.feature(utmZone).geometry, turf.feature(county).geometry)) {
        for (let k in utmZoneTiles[utmZone.properties.UTM_ZONE].features) {
          const tile = utmZoneTiles[utmZone.properties.UTM_ZONE].features[k]
          console.log(`(${i}/${counties.features.length})(${j})(${k}/${utmZoneTiles[utmZone.properties.UTM_ZONE].features.length}) Checking ${county.properties.NAME} tile x:${tile.properties.Name_X} y:${tile.properties.Name_Y}`)

          if (turf.booleanIntersects(turf.feature(tile).geometry, turf.feature(county).geometry)) {
            tiles.push(tile)
          }
        }
      }
    }

    if (!fs.existsSync(`./${county.properties.STATE}`)) {
      fs.mkdirSync(`./${county.properties.STATE}`)
    }

    console.log(`Writing ${county.properties.STATE}/${county.properties.NAME}.json`)
    fs.writeFileSync(`./${county.properties.STATE}/${county.properties.NAME}.json`, JSON.stringify({ type: 'FeatureCollection', features: tiles }, null, 2))
  // }
}

main()