const countyProjects = require('#data/County_Lidar_Project_Properties.json')
const fs = require('fs')

const main = async () => {
  const newCountyProjects = []

  for (let cp of countyProjects) {
    newCountyProjects.push({
      ...cp,
      start_date: new Date(cp.collect_start).toISOString(),
      end_date: new Date(cp.collect_end).toISOString()
    })
  }

  fs.writeFileSync('../../data/County_Lidar_Project_Properties.json', JSON.stringify(newCountyProjects, null, 2))
}

main()