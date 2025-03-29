const spcsZones = require('../SPCS_Grids/SPCS_Zones.json')
const utmZones = require('../UTM_Grids/UTM_Zones.json')
const defs = require('./defs.json')
const coordinateSystems = require('./coordinate_systems.json')
const fs = require('fs')

const main = async () => {
  let contents = "export const addDefs = (proj4) => {";

  for (let zone of spcsZones.features) {
    const url = `https://epsg.io/${zone.properties.SPCS_ID}.proj4js`
    console.log('Fetching', url)
    const response = await fetch(url)
    const proj4str = await response.text()
    console.log(proj4str)

    contents += '\n'
    contents += proj4str
  }

  for (let zone of utmZones.features) {
    const zoneNumber = zone.properties.UTM_ZONE
    const csName = `NAD83(2011) / UTM zone ${zoneNumber}N`
    const cs = coordinateSystems.find(cs => cs.name === csName)
    const def = defs.find(d => d[0] === `${cs.id.authority}:${cs.id.code}`)
    
    const proj4str = `proj4.defs("${cs.id.authority}:${cs.id.code}","${def[1]}");`
    console.log(proj4str)

    contents += '\n'
    contents += proj4str
  }

  contents += '\n'
  contents += '}'


  console.log('Writing to file')
  fs.writeFileSync('./defs.js', contents)
}

main()