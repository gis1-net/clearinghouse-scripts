const utmZones = require('./UTM_Zones.json')
const counties = require('../SPCS_Grids/US_Counties_Detailed.json')
const { execSync } = require('child_process');
const { groupBy } = require('lodash')
const turf = require('@turf/turf')
const fs = require('fs')

const main = async () => {
  const grouped = {}

  for (let county of counties.features) {
    console.log(`Processing ${county.properties.NAME}, ${county.properties.STATE}`)
    if (!(county.properties.STATE in grouped)) {
      grouped[county.properties.STATE] = {}
    }

    if (!(county.properties.UTM_ZONE in grouped[county.properties.STATE])) {
      grouped[county.properties.STATE][county.properties.UTM_ZONE] = county.geometry
    } else {
      const fc = turf.featureCollection([
        turf.feature(grouped[county.properties.STATE][county.properties.UTM_ZONE]), 
        turf.feature(county.geometry)
      ])
      const union = turf.union(fc)
      grouped[county.properties.STATE][county.properties.UTM_ZONE] = union.geometry
    }
  }

  for (let state in grouped) {
    const features = []

    for (let zone in grouped[state]) {
      const feature = {
        type: 'Feature',
        properties: {
          STATE: state,
          UTM_ZONE: zone
        },
        geometry: grouped[state][zone]
      }


      console.log(`Writing ./SP_UTM_Grids/${state}/${zone}.geojson`)
  
      fs.mkdirSync(`./SP_UTM_Grids/${state}`, { recursive: true })
      fs.writeFileSync(`./SP_UTM_Grids/${state}/${zone}.geojson`, JSON.stringify({ type: 'FeatureCollection', features: [feature] }, null, 2))
    }
  }
}

if (require.main === module) {
  main()
}

module.exports = main