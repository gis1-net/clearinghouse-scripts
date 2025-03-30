const spcsZones = require('./SPCS_Zones.json')
const { execSync } = require('child_process');

const main = async () => {
  for (let zone of spcsZones.features) {
    const state = zone.properties.STATE.replaceAll(' ', '\\ ')
    const zoneName = zone.properties.SP_ZONE.replaceAll(' ', '_')
    const projection = `${zone.properties.SPCS_AUTH}:${zone.properties.SPCS_ID}`

    const inputPath = `./SPCS_Grids_RAW/${state}/${zoneName}_Grid.geojson`
    const outputPath = `./SPCS_Grids_RAW/${state}/${zoneName}.shapefile`
    
    console.log(`Reprojecting ${zoneName}`)
    const command = `ogr2ogr -f "ESRI Shapefile" -skipfailures ${outputPath} ${inputPath} -t_srs ${projection}`
    execSync(command)
  }
}

if (require.main === module) {
  main()
}

module.exports = main