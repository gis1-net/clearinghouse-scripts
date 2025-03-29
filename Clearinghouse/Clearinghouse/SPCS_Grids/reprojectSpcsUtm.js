const spcsZones = require('./SPCS_Zones.json')
const { execSync } = require('child_process');
const fs = require('fs')

const main = async () => {
  const stateFiles = fs.readdirSync('./State_SPCS_UTM').filter(f => f.endsWith('.geojson'))

  for (let stateFile of stateFiles) {
    const state = stateFile.split('.')[0].replaceAll(' ', '\\ ')

    const inputPath = `./State_SPCS_UTM/${state}.geojson`
    const outputPath = `./State_SPCS_UTM/${state}.shapefile`
    
    console.log(`Reprojecting ${state}`)
    const command = `ogr2ogr -f "ESRI Shapefile" -skipfailures ${outputPath} ${inputPath}`
    execSync(command)
  }
}

if (require.main === module) {
  main()
}

module.exports = main