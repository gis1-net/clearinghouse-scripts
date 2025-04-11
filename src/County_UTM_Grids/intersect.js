const counties = require('#data/US_Counties_Detailed.json')
const utmZones = require('#data/UTM_Zones.json')
const turf = require('@turf/turf')
const fs = require('fs')
const utmZoneTiles = []

const main = async () => {
  const i = process.argv[2]

  // for (let i in counties.features) {
    const county = counties.features[i]
    console.log(`(${i}/${counties.features.length}) Checking ${county.properties.NAME} ${county.properties.LSAD}`)
    const tiles = []

    for (let j in utmZones.features) {
      const utmZone = utmZones.features[j]

      const countyGeometry = turf.buffer(turf.feature(county).geometry, .3, { units: "kilometers" })

      if (turf.booleanIntersects(turf.feature(utmZone).geometry, countyGeometry)) {
	      utmZoneTiles[utmZone.properties.UTM_ZONE] = require(`#data/UTM_Grids/${utmZone.properties.UTM_ZONE}.json`)

        for (let k in utmZoneTiles[utmZone.properties.UTM_ZONE].features) {
          const tile = utmZoneTiles[utmZone.properties.UTM_ZONE].features[k]
          console.log(`(${i}/${counties.features.length})(${j})(${k}/${utmZoneTiles[utmZone.properties.UTM_ZONE].features.length}) Checking ${county.properties.NAME} ${county.properties.LSAD} tile x:${tile.properties.Name_X} y:${tile.properties.Name_Y}`)

          if (turf.booleanIntersects(turf.feature(tile).geometry, countyGeometry)) {
            tiles.push(tile)
          }
        }
      }
    }

    if (!fs.existsSync(`${__dirname}/../../data/County_UTM_Grids/${county.properties.STATE}`.replaceAll(' ', '_'))) {
      fs.mkdirSync(`${__dirname}/../../data/County_UTM_Grids/${county.properties.STATE}`.replaceAll(' ', '_'), { recursive: true })
    }

    console.log(`Writing ${county.properties.STATE}/${county.properties.NAME}_${county.properties.LSAD}.json`.replaceAll(' ', '_'))
    fs.writeFileSync(`${__dirname}/../../data/County_UTM_Grids/${county.properties.STATE}/${county.properties.NAME}_${county.properties.LSAD}.json`, JSON.stringify({ type: 'FeatureCollection', features: tiles }, null, 2))
  // }
}

main()
