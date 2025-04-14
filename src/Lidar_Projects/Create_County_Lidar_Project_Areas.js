const countyProjects = require('#data//County_Lidar_Projects.json')
const counties = require('#data/US_Counties_Detailed.json')
const projects = require('#data/USGS_Projects.json')
const turf = require('@turf/turf')
const { uniqBy } = require('lodash')
const fs = require('fs')

const main = async () => {
  const newCountyProjects = []

  for (let countyProject of uniqBy(countyProjects, cp => `${cp.county}:${cp.lsad}:${cp.project}`)) {
    const county = counties.features.find(county => county.properties.NAME === countyProject.county && county.properties.LSAD === countyProject.lsad && county.properties.STATE === countyProject.state)
    const project = projects.features.find(project => project.properties.OBJECTID === countyProject.OBJECTID)

    console.log(`Processing ${county.properties.NAME} ${county.properties.LSAD} + ${project.properties.project}`)

    const intersect = turf.intersect(turf.featureCollection([turf.feature(county).geometry, turf.feature(project).geometry]))

    if (intersect) {
      const newCountyProject = {
        properties: {...countyProject},
        geometry: intersect.geometry
      }

      delete newCountyProject.properties.OBJECTID
      
      newCountyProjects.push(newCountyProject)
    }
  }

  console.log('Writing to file')
  fs.writeFileSync('../../data/County_Lidar_Project_Areas.json', JSON.stringify({ type: 'FeatureCollection', features: newCountyProjects}, null, 2))
}

main()