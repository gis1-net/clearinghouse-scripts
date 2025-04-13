const fs = require('fs')
const { uniqBy } = require('lodash')

const url = "https://api.maptiler.com/coordinates/search/NAD83+2011.json?key=KKnE3zHz7eaiaycdl1R0&limit=50&offset={OFFSET}"

const main = async () => {
  const coordinateSystems = []

  for (let i = 0; i < 680; i += 40) {
    const response = await fetch(url.replace('{OFFSET}', i))
    const json = await response.json()

    coordinateSystems.push(...json.results)
  }

  console.log('Writing to file')
  fs.writeFileSync('../../data/Coordinate_Systems/coordinate_system_details.json', JSON.stringify(uniqBy(coordinateSystems, cs => cs.id.code), null, 2))
}

main()