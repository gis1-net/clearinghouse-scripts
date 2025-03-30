const coordinateSystems = require('../EPSG/coordinate_systems')
const utmZones = require('./UTM_Zones')
const proj4 = require('proj4')
const { addDefs } = require('../EPSG/defs.js')
const fs = require('fs')
const turf = require('@turf/turf')

addDefs(proj4)

const main = async () => {
  for (let zone of utmZones.features) {
    const zoneNumber = zone.properties.UTM_ZONE
    const coordinateSystem = coordinateSystems.find(cs => cs.name === `NAD83(2011) / UTM zone ${zoneNumber}N`)
    const utmcs = `${coordinateSystem.id.authority}:${coordinateSystem.id.code}`
    
    const sw = zone.geometry.coordinates[0][1]
    const utmSw = proj4(utmcs).forward(sw)
    const utmSwRound = [Math.floor(utmSw[0] / 10000) * 10000, utmSw[1]]

    const se = zone.geometry.coordinates[0][0]
    const utmSe = proj4(utmcs).forward(se)
    const utmSeRound = [Math.ceil(utmSe[0] / 10000) * 10000, utmSe[1]]

    const ne = zone.geometry.coordinates[0][3]
    const utmNe = proj4(utmcs).forward(ne)
    const utmNeRound = [Math.ceil(utmNe[0] / 10000) * 10000, Math.ceil(utmNe[1] / 10000) * 10000]

    const features = []
    
    console.log('Creating tiles for UTM Zone', zoneNumber)

    for (let x = utmSwRound[0] - 500000; x < utmSeRound[0] + 500000; x += 10000) {
      for (let y = 0; y < utmNeRound[1]; y += 10000) {
        console.log(x, y)
        const feature = {
          type: 'Feature',
          properties: {
            X_value: x,
            Y_value: y + 10000,
            Name_X: (x < 0 ? '-' : '') + Math.abs(x).toString().padStart(6, '0').substring(0, 2),
            Name_Y: (y + 10000).toString().padStart(7, '0').substring(0, 3),
            Tile_Name: ''
          },
          geometry: {
            type: 'Polygon',
            coordinates: [[
              proj4(utmcs).inverse([x, y]),
              proj4(utmcs).inverse([x, y + 10000]),
              proj4(utmcs).inverse([x + 10000, y + 10000]),
              proj4(utmcs).inverse([x + 10000, y]),
              proj4(utmcs).inverse([x, y])
            ]]
          }
        }

        features.push(feature)
      }
    }

    fs.writeFileSync(`./UTM_Grids/${zoneNumber}.json`, JSON.stringify({ type: 'FeatureCollection', features }, null, 2))
  }
}

if (require.main === module) {
  main()
}

module.exports = main