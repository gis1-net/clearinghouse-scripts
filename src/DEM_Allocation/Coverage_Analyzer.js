const turf = require('@turf/turf')

const analyzeCoverage = (county, project) => {
    const intersect = turf.intersect(turf.featureCollection([turf.feature(county).geometry, turf.feature(project).geometry]))

    let coverage = 0

    if (intersect) {
        const intersectArea = turf.area(intersect)
        const countyArea = turf.area(county)
        coverage = intersectArea / countyArea
    }

    return coverage
}

module.exports = { analyzeCoverage }