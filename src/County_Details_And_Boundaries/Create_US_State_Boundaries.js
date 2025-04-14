const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const turf = require('@turf/turf')
const { groupBy } = require('lodash')

const counties = readJsonData('US_County_Details_And_Boundaries.geojson')

const main = async () => {
  const grouped = groupBy(counties.features, c => c.properties.STATE)

  const stateFeatures = []

  for (let state in grouped) {
    const counties = grouped[state]

    if (counties.length > 1) {
      const stateFeature = turf.union(turf.featureCollection(counties.map(c => turf.feature(c).geometry)))
      stateFeatures.push({
        ...stateFeature,
        properties: { name: state }
      })
    } else {
      stateFeatures.push({
        properties: { name: state },
        geometry: counties[0].geometry
      })
    }
  }

  writeJsonData('US_State_Boundaries.geojson', { type: 'FeatureCollection', features: stateFeatures })
}

main()