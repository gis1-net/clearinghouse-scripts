const fs = require('fs')

const listAvailableDems = async (projects) => {
  const pattern = /x[\d]{2}y[\d]{3}/g

  const dir = `${__dirname}/../../data/DEM_Download_Lists/${state}`

  const tiles = []

  for (let project of projects) {
    const contents = fs.readFileSync(`${dir}/${project}.txt`).toString()

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
  }

  return tiles
}

module.exports = { listAvailableDems }