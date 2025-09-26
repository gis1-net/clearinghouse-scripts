const counties = require('#data/US_Counties_Detailed.json')
const { groupBy } = require('lodash')
const fs = require('fs')
const { execSync } = require('child_process');

const main = async () => {
    const stateGroups = groupBy(counties.features, c => c.properties.STATE)

    for (let state in stateGroups) {
        const counties = stateGroups[state]

        const inputPath = `../../data/State_Counties_Detailed/${state.replaceAll(' ', '_')}.json`
        const outputPath = `../../data/State_Counties_Detailed/${state.replaceAll(' ', '_')}.shapefile`

        fs.writeFileSync(inputPath, JSON.stringify({ type: 'FeatureCollection', features: counties }, null, 2))
        
        const command = `ogr2ogr -f "ESRI Shapefile" -skipfailures ${outputPath} ${inputPath}`
        execSync(command)
        
        fs.renameSync(`${outputPath}/${state.replaceAll(' ', '_')}.shp`, `../../data/State_Counties_Detailed/${state.replaceAll(' ', '_')}.shp`)
        fs.renameSync(`${outputPath}/${state.replaceAll(' ', '_')}.prj`, `../../data/State_Counties_Detailed/${state.replaceAll(' ', '_')}.prj`)
        fs.renameSync(`${outputPath}/${state.replaceAll(' ', '_')}.shx`, `../../data/State_Counties_Detailed/${state.replaceAll(' ', '_')}.shx`)
        fs.renameSync(`${outputPath}/${state.replaceAll(' ', '_')}.dbf`, `../../data/State_Counties_Detailed/${state.replaceAll(' ', '_')}.dbf`)
        fs.rmdirSync(outputPath)
    }
}

main()