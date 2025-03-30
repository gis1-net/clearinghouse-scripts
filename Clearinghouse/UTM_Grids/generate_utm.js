const fs = require('fs')
const coordinateSystems = require('../EPSG/coordinate_systems.json')

const main = async () => {
  const features = []

  let utmZone = 19;

  for (let x = -66; x > -180; x -= 6) {
    const cs = coordinateSystems.find(cs => cs.name === `NAD83(2011) / UTM zone ${utmZone}N`)

    const feature = {
      type: 'Feature',
      properties: {
        UTM_ZONE: utmZone--,
        CS_AUTH: cs.id.authority,
        CS_ID: cs.id.code
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [x, 0],
          [x - 6, 0],
          [x - 6, 72],
          [x, 72],
          [x, 0]
        ]]
      }
    }

    features.push(feature)
  }

  fs.writeFileSync('./UTM_Zones.json', JSON.stringify({ type: 'FeatureCollection', features }, null, 2))
}

if (require.main === module) {
  main()
}

module.exports = main