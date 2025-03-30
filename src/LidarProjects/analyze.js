const lidarProjects = require('./USGS_Projects.json')

const main = async () => {
  for (let project of lidarProjects.features) {
    if (project.properties.ql === 'Other') {
      console.log(new Date(project.properties.collect_start))
    }
  }
}

main()