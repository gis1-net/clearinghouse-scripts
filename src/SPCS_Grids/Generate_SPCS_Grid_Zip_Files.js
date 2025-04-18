const fs = require('fs')
const { groupBy } = require('lodash')
const { execSync } = require('child_process');

const main = async () => {
  const folders = fs.readdirSync('../../data/SPCS_Grids')
  
  for (let folder of folders) {
    const files = fs.readdirSync(`../../data/SPCS_Grids/${folder}`)
    
    const groups = groupBy(files, f => f.split('.')[0])

    for (let group in groups) {
      if (fs.existsSync(`../../data/SPCS_Grids/${folder}/${group}.dbf`)) {
        execSync(`zip ../../data/SPCS_Grids/${group}.zip ../../data/SPCS_Grids/${folder}/${group}.dbf ../../data/SPCS_Grids/${folder}/${group}.shp ../../data/SPCS_Grids/${folder}/${group}.shx ../../data/SPCS_Grids/${folder}/${group}.prj`)
      }
    }
  }
}

main()