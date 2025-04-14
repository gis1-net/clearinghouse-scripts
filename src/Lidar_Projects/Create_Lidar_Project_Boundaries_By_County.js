const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const turf = require('@turf/turf')

const counties = readJsonData('US_County_Details_And_Boundaries.geojson')

const main = async () => {
  for (let county of counties.features) {
    const matchingProjects = []

    const countyBoundary = turf.buffer(turf.feature(county).geometry, .3, { units: "kilometers" })

    const stateLidarProjects = readJsonData(`Lidar_Project_Boundaries_By_State/${county.properties.STATE}_Lidar_Project_Boundaries.geojson`)
    
    for (let lidarProject of stateLidarProjects.features) {
      console.log(`[${county.properties.NAME}, ${county.properties.STATE}] Checking ${lidarProject.properties.workunit}`)
      if (turf.booleanIntersects(countyBoundary, lidarProject.geometry)) {
        matchingProjects.push(lidarProject)
      }
    }

    writeJsonData(`Lidar_Project_Boundaries_By_County/${county.properties.STATE}/${county.properties.NAME}_${county.properties.LSAD}_Lidar_Project_Boundaries.geojson`, { type: 'FeatureCollection', features: matchingProjects})
  }
}

main()