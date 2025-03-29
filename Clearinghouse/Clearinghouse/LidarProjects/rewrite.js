const countyProjects = require('./County_Projects.json')
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

  fs.writeFileSync('County_Projects_New.json', JSON.stringify(newCountyProjects, null, 2))
}

main()