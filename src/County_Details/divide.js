const counties = require('#data/US_Counties_Detailed.json')
const { groupBy } = require('lodash')
const fs = require('fs')

const main = async () => {
    const stateGroups = groupBy(counties.features, c => c.properties.STATE)

    for (let state in stateGroups) {
        const counties = stateGroups[state]

        fs.writeFileSync(`../../data/State_Counties_Detailed/${state}.json`, JSON.stringify({ type: 'FeatureCollection', featuers: counties }, null, 2))
        
    }
}

main()