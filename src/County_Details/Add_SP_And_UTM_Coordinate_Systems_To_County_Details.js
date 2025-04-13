const counties = require('#data/US_Counties_Detailed.json')
const coordinateSystems = require('#data/Coordinate_Systems/coordinate_systems.json')
const fs = require('fs')

const main = async () => {
    const newFeatures = []

    for (let county of counties.features) {
        const spcs = coordinateSystems.find(cs => cs.id.code === parseInt(county.properties.SPCS_ID))
        const utmcs = coordinateSystems.find(cs => cs.name === `NAD83(2011) / UTM zone ${county.properties.UTM_ZONE}N`)

        if (!spcs || !utmcs) {
            console.log(county)
        }
        
        const data = {
            ...county
        }

        delete data.properties.SPCS_ID

        data.properties.FULL_NAME = `${county.properties.NAME}_${county.properties.LSAD}`.replaceAll(' ', '_')
        data.properties.SPCS_AUTH = spcs.id.authority,
        data.properties.SPCS_ID = spcs.id.code,
        data.properties.UTMCS_AUTH = utmcs.id.authority,
        data.properties.UTMCS_ID = utmcs.id.code

        newFeatures.push(data)
    }

    fs.writeFileSync('../../data/US_Counties_Detailed_2.json', JSON.stringify({ type: 'FeatureCollection', features: newFeatures }, null, 2))
}

main()