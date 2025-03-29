const utmZones = require('./UTM_Zones.json')
const { execSync } = require('child_process');

const main = async () => {
  for (let zone of utmZones.features) {
    const zoneNumber = zone.properties.UTM_ZONE
    const projection = `${zone.properties.CS_AUTH}:${zone.properties.CS_ID}`

    const inputPath = `./UTM_Grids/${zoneNumber}.geojson`
    const outputPath = `./UTM_Grids/${zoneNumber}.shapefile`
    
    console.log(`Reprojecting ${zoneNumber}`)
    const command = `ogr2ogr -f "ESRI Shapefile" -skipfailures ${outputPath} ${inputPath} -t_srs ${projection}`
    execSync(command)
  }
}

if (require.main === module) {
  main()
}

module.exports = main