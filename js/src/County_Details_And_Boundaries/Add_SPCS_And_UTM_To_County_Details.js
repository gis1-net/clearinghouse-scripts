const { readCSVSync } = require("read-csv-sync")
const counties = require('./US_Counties.json')
const { keyBy } = require('lodash')
const coordinateSystems = require('../EPSG/coordinate_systems.json')
const fs = require('fs')

const transformEmpty = (value) => {
  if (value === '') {
    return null
  }
  return value
}

const main = async () => {
  const countyReferences = keyBy(readCSVSync('./state_plane_reference.csv'), c => parseInt(c.fips))
  const countyEpsgs = keyBy(readCSVSync('./2021-spcs-epsg.csv'), c => parseInt(c["Zone FIPS"]))
  const coordinateSystemsKeyed = keyBy(coordinateSystems, cs => parseInt(cs.id.code))

  const newCounties = []

  for (let county of counties.features) {
    const geoId = county.properties.GEO_ID
    const fipsId = parseInt(geoId.split('US')[1])
    const countyReference = countyReferences[fipsId]
    const fipsZoneId = parseInt(countyReference.nad83_fz)
    const statePlaneZone = countyEpsgs[fipsZoneId]
    const coordinateSystemId = transformEmpty(statePlaneZone["NAD 83 (2011) Intl Feet"]) ?? transformEmpty(statePlaneZone["NAD 83 (2011) US Feet"]) ?? transformEmpty(statePlaneZone["NAD 83 US Feet"])
    const coordinateSystem = coordinateSystemsKeyed[parseInt(coordinateSystemId)]

    if (!coordinateSystem) {
      console.log(`ERROR COORDINATE SYSTEM NOT FOUND FOR ${county.properties.NAME}, ${county.properties.STATE}`)
    }

    const newCounty = {
      ...county,
      properties: {
        ...county.properties,
        SPCS_AUTH: coordinateSystem.id.authority,
        SPCS_ID: coordinateSystemId,
        SPCS_NAME: coordinateSystem.name,
        SPCS_UNIT: coordinateSystem.unit,
        SP_ZONE: countyReference.nad83_zone,
        UTM_ZONE: countyReference.utm_zone,
      }
    }

    newCounties.push(newCounty)
  }

  fs.writeFileSync('US_Counties_Detailed.json', JSON.stringify({ type: 'FeatureCollection', features: newCounties }, null, 2))
}

if (require.main === module) {
  main()
}

module.exports = main