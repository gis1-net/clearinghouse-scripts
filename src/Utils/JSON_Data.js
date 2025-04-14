const fs = require('fs')

const readJsonData = (path) => JSON.parse(fs.readFileSync(`${__dirname}/../../data/${path}`))

const writeJsonData = (path, data, minify = false) => {
  const parts = path.split('/')
  parts.pop()

  const directory = `../../data/${parts.join('/')}`
  if (!fs.existsSync(directory)) {
    fs.mkdirSync(directory, true)
  }

  console.log(`Writing data/${path}`)
  fs.writeFileSync(`${__dirname}/../../data/${path}`, JSON.stringify(data, minify ? undefined : null, minify ? undefined : 2))
}

module.exports = { readJsonData, writeJsonData }