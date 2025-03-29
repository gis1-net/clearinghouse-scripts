const counties = require('./US_Counties_Detailed.json')
const { groupBy } = require('lodash')
const turf = require('@turf/turf')
const fs = require('fs')

const main = async () => {
  const grouped = groupBy(counties.features, c => c.properties.SPCS_ID)

  const zones = []

  for (let spcsId in grouped) {
    console.log(spcsId)
    const features = grouped[spcsId]

    const polygons = features.map(f => turf.feature(f.geometry))
    const spcz = polygons.length > 1
      ? turf.union(turf.featureCollection(polygons))
      : polygons[0]

    const zone = {
      type: 'Feature',
      properties: {
        STATE: features[0].properties.STATE,
        SPCS_AUTH: features[0].properties.SPCS_AUTH,
        SPCS_ID: spcsId,
        SPCS_NAME: features[0].properties.SPCS_NAME,
        SPCS_UNIT: features[0].properties.SPCS_UNIT,
        SP_ZONE: features[0].properties.SP_ZONE
      },
      geometry: spcz.geometry
    }

    zones.push(zone)
  }

  fs.writeFileSync('./SPCS_Zones.json', JSON.stringify({ type: 'FeatureCollection', features: zones }, null, 2))
}

if (require.main === module) {
  main()
}

module.exports = main