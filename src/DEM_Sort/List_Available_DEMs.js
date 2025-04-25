const fs = require('fs')

const listAvailableDems = async (state, project) => {
  const pattern = /x[\d]{2}y[\d]{3}/g

  const indexFile = `${__dirname}/../../data/DEM_List/${state}/${project}.txt`

  const contents = fs.readFileSync(indexFile).toString()

  const lines = contents.split('\n')

  for (let line of lines) {
    const match = line.match(pattern)
    if (match) {
      tiles.push({
        x: parseInt(match.toString().substring(1, 3)),
        y: parseInt(match.toString().substring(4, 7)),
        project: line.split('/')[7],
        url: line
      })
    }
  }

  return tiles
}

module.exports = { listAvailableDems }