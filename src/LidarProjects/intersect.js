const turf = require("@turf/turf")
const counties = require("./US_Counties.json")
const projects = require("./USGS_Projects.json")
const fs = require('fs')

const main = async () => {
  const startLetter = process.argv[2]

  const countyProjects = []

  for (const county of counties.features) {
    if (county.properties.NAME[0] === startLetter) {
      const countyFeature = turf.feature(county)
      
      for (const project of projects.features) {
        console.log('Checking', county.properties.NAME, '+', project.properties.project)

        const projectFeature = turf.feature(project)

        const intersect = turf.intersect(turf.featureCollection([countyFeature.geometry, projectFeature.geometry]))

        if (intersect) {
          const countyProject = {
            county: county.properties.NAME,
            state: county.properties.STATE,
            ...project.properties
          }

          countyProjects.push(countyProject)
        }
      }
    }
  }

  console.log('Writing to file')
  fs.writeFileSync(`county_projects_${startLetter}.json`, JSON.stringify(countyProjects, null, 2))
}

main()