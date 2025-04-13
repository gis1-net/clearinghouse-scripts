const projectFeaturesRaw = require('./project_features_raw.json')
const { uniqBy } = require('lodash')
const fs = require('fs')

const main = async () => {
  let features = uniqBy(projectFeaturesRaw, f => f.properties.OBJECTID)

  features = features.filter(f => ['QL 0', 'QL 1', 'QL 2'].includes(f.properties.ql))

  // features = uniqBy(features, f => f.properties.ql)

  // console.log(features.map(f => f.properties.ql))

  console.log(projectFeaturesRaw.length, features.length)

  fs.writeFileSync('./project_features.json', JSON.stringify({ type: "FeatureCollection", features }, null, 2))  
}

main();