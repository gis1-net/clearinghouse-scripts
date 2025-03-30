const coordinateSystems = require('./coordinate_systems.json')
const { uniqBy } = require('lodash')

const main = async () => {
  console.log(coordinateSystems.length)
}

main()