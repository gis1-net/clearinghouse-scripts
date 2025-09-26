const { readJsonData } = require('#src/Utils/JSON_Data.js')
const fs = require('fs')


const main = (state) => {
  const demAllocations = readJsonData(`DEM_Allocation/${state.replaceAll(' ', '_')}.json`)

  const stateProjects = new Set()

  for (let county of demAllocations) {
    if (county.projects_1) {
      const countyProjects = county.projects_1.split('|')
      for (let project of countyProjects) {
        if (fs.existsSync(`${__dirname}/../../data/DEM_Download_Lists/${project}.txt`)) {
          const file = fs.readFileSync(`${__dirname}/../../data/DEM_Download_Lists/${project}.txt`, 'utf-8')
          const lines = file.split('\n')

          for (let line of lines) {
            const fileName = line.split('/').pop()
            if (!fs.existsSync(`/mnt/z/${state.replaceAll(' ', '_').toUpperCase()}/Tif_Files_UTM/${project}/${fileName}`)) {
              console.log(`${project}/${fileName} DOES NOT EXIST`)
            }
          }
        }
      }
    }
  }
}

if (require.main === module) {
  main(...process.argv.slice(2))
}
