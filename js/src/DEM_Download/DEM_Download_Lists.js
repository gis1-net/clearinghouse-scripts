const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const fs = require('fs')
const LidarProjects = readJsonData('Lidar_Project_Boundaries.geojson')

const main = async () => {
  for (let project of LidarProjects.features) {
    if (project.properties.sourcedem_link) {
      const contents = fs.readFileSync(`../../data/DEM_Download_Lists/${project.properties.workunit}.txt`, 'utf-8')

      if (contents.startsWith('<?xml')) {
        const url = `${project.properties.sourcedem_link.replaceAll('index.html?prefix=', '')}/0_file_download_links.txt`

        console.log(`Fetching ${url}`)
        
        const response = await fetch(url)

        fs.writeFileSync(`../../data/DEM_Download_Lists/${project.properties.workunit}.txt`, await response.text())
      }
    }
  }
}

main()