const proj4 = require('proj4')
const defs = require('./defs.json')
const features = require('./project_features.json')
const fs = require('fs')

const main = async () => {
  const coordinateSystems = defs.map(def => `${def[0]}`)
  
  const transformedFeatures = []

  for (let feature of features.features) {
    console.log('Transforming feature', feature.properties.OBJECTID)
    const transformedFeature = {
      ...feature,
      geometry: {
        type: feature.geometry.rings.length > 1 ? "MultiPolygon" : "Polygon",
        coordinates: feature.geometry.rings.length > 1
          ? feature.geometry.rings.map(ring => [ ring.map(coords => proj4('EPSG:3857').inverse(coords)) ])
          : feature.geometry.rings.map(ring => ring.map(coords => proj4('EPSG:3857').inverse(coords)))
      }
    }

    // console.log(new Date(feature.properties.collect_start))

    // console.log(transformedFeature)

    transformedFeatures.push(transformedFeature)
  }

  console.log('Writing to file')
  fs.writeFileSync('transformed_features.json', JSON.stringify({ type: 'FeatureCollection', features: transformedFeatures}, null, 2))
}

main()