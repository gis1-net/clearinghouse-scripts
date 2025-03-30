const counties = require('./US_Counties_Detailed.json')
const { groupBy } = require('lodash')
const fs = require('fs')

const main = async () => {
  const countiesByState = groupBy(counties.features, c => c.properties.STATE)

  for (let state in countiesByState) {
    const countyFeatures = countiesByState[state].map(c => ({
      ...c,
      properties: {
        NAME: c.properties.NAME,
        LSAD: c.properties.LSAD,
        SP_Zone: c.properties.SP_ZONE,
        UTM_Zone: c.properties.UTM_ZONE
      }
    }))

    fs.writeFileSync(`State_SPCS_UTM/${state}.geojson`, JSON.stringify({ type: 'FeatureCollection', features: countyFeatures }, null, 2))
  }
}

main()