const turf = require("@turf/turf")
const counties = require("#data/US_Counties_Detailed.json")
const projects = require("#data/USGS_Projects.json")
const fs = require('fs')

const main = async () => {
  const countyProjects = []

  for (const county of counties.features) {    
    for (const project of projects.features) {
      console.log(`Checking ${county.properties.NAME} ${county.properties.LSAD} + ${project.properties.project}`)
      
      const intersect = turf.booleanIntersects(county.geometry, project.geometry)

      if (intersect) {
        const countyProject = {
          county: county.properties.NAME,
          lsad: county.properties.LSAD,
          state: county.properties.STATE,
          ...project.properties
        }

        countyProjects.push(countyProject)
      }
    }
  }

  console.log('Writing to file')
  fs.writeFileSync(`../../data/County_Lidar_Project_Properties.json`, JSON.stringify(countyProjects, null, 2))
}

main()