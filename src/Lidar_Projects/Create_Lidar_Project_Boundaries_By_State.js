const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const turf = require('@turf/turf')

const states = readJsonData('US_State_Boundaries.geojson')
const lidarProjects = readJsonData('Lidar_Project_Boundaries.geojson')

const main = async (i) => {
  const state = states.features[i]
  const matchingProjects = []

  console.log(`Checking ${state.properties.name}`)
  const stateBoundary = turf.buffer(turf.feature(state.geometry).geometry, .3, { units: "kilometers" })
  
  for (let lidarProject of lidarProjects.features) {
    console.log(`[${state.properties.name}] Checking ${lidarProject.properties.workunit}`)
    if (turf.booleanIntersects(stateBoundary, lidarProject.geometry)) {
      matchingProjects.push(lidarProject)
    }
  }

  writeJsonData(`Lidar_Project_Boundaries_By_State/${state.properties.name}_Lidar_Project_Boundaries.geojson`, { type: 'FeatureCollection', features: matchingProjects})
}

main(process.argv[2])