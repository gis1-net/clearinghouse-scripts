const spcsZones = require('../../data/SPCS_Zones.json')
const { execSync } = require('child_process');
const fs = require('fs')

const main = async () => {
  for (let zone of spcsZones.features) {
    const state = zone.properties.STATE.replaceAll(' ', '_')
    const zoneName = zone.properties.SP_ZONE.replaceAll(' ', '_')
    const projection = `${zone.properties.SPCS_AUTH}:${zone.properties.SPCS_ID}`

    const inputPath = `../../data/SPCS_Grids/${state}/${zoneName}_Grid.geojson`
    const outputPath = `../../data/SPCS_Grids/${state}/${zoneName}.shapefile`
    
    console.log(`Reprojecting ${zoneName}`)
    const command = `ogr2ogr -f "ESRI Shapefile" -skipfailures ${outputPath} ${inputPath} -t_srs ${projection}`
    execSync(command)
    
    fs.renameSync(`${outputPath}/${zoneName}_Grid.shp`, `../../data/SPCS_Grids/${state}/${zoneName}_Grid.shp`)
    fs.renameSync(`${outputPath}/${zoneName}_Grid.prj`, `../../data/SPCS_Grids/${state}/${zoneName}_Grid.prj`)
    fs.renameSync(`${outputPath}/${zoneName}_Grid.shx`, `../../data/SPCS_Grids/${state}/${zoneName}_Grid.shx`)
    fs.renameSync(`${outputPath}/${zoneName}_Grid.dbf`, `../../data/SPCS_Grids/${state}/${zoneName}_Grid.dbf`)
    fs.rmdirSync(outputPath)
  }
}

if (require.main === module) {
  main()
}

module.exports = main