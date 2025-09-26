const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { groupBy, keyBy } = require('lodash')
const { Worker } = require("worker_threads");
const counties = readJsonData('US_County_Details_And_Boundaries.geojson')
const ObjectsToCsv = require('objects-to-csv');
const projects = keyBy(readJsonData('Lidar_Project_Boundaries.geojson').features, p => p.properties.workunit)
const coordinateSystems = keyBy(readJsonData('Coordinate_Systems/coordinate_system_details_new.json'), cs => `${cs.id.code}`)

const jobs = []
const data = []

const createWorker = async () => {
  while (jobs.length) {
    const job = jobs.shift()

    const response = await new Promise((resolve, reject) => {
      const worker = new Worker(`${__dirname}/Allocate_DEM_Files_Thread.js`, {
        workerData: { index: job },
      });
      worker.on("message", (res) => {
        resolve(res);
      });
      worker.on("error", (msg) => {
        reject(`An error ocurred: ${msg}`);
      });
    })

    data.push(response)
  }
}

const main = async (numThreads, state) => {
  const workerPromises = []

  for (let i = 0; i < 3143; i++) {
    if (counties.features[i].properties.STATE === state.replaceAll('_', ' '))
    jobs.push(i)
  }

  for (let i = 0; i < numThreads; i++) {
    workerPromises.push(createWorker(i))
  }

  await Promise.all(workerPromises)

  const stateGroups = groupBy(data, d => d.state)

  // const stateGroups = {
  //   Virginia: readJsonData(`DEM_Allocation/${state.replaceAll(' ', '_')}.json`)
  // }

  for (let state in stateGroups) {
    writeJsonData(`DEM_Allocation/${state.replaceAll(' ', '_')}.json`, stateGroups[state])

    const csvData = []

    for (let county of stateGroups[state]) {
      for (let groupNumber in county.groups) {
        const group = county.groups[groupNumber]

        const horizontalCrs = group.map(project => {
          const crs = `${projects[project].properties.horiz_crs}`
          return coordinateSystems[crs]?.name ?? 'Unknown'
        })
        const horizontalUnits = group.map(project => {
          const crs = `${projects[project].properties.horiz_crs}`
          return coordinateSystems[crs]?.unit ?? 'Unknown'
        })
        const verticalCrs = group.map(project => {
          const crs = `${projects[project].properties.vert_crs}`
          return coordinateSystems[crs]?.name ?? 'Unknown'
        })
        const verticalUnits = group.map(project => {
          const crs = `${projects[project].properties.vert_crs}`
          return coordinateSystems[crs]?.unit ?? 'Unknown'
        })

        csvData.push({
          name: `${county.name}${groupNumber > 0 ? groupNumber : ''}`,
          lsad: county.lsad,
          groupNumber: groupNumber + 1,
          state: county.state,
          projects: group.join('|'),
          horizontal_crs: horizontalCrs.join('|'),
          horizontal_units: horizontalUnits.join('|'),
          vertical_crs: verticalCrs.join('|'),
          vertical_units: verticalUnits.join('|')
        })
      }
    }

    console.log(`Writing DEM_Allocation/${state.replaceAll(' ', '_')}.csv`)
    const csv = new ObjectsToCsv(csvData)
    await csv.toDisk(`${__dirname}/../../data/DEM_Allocation/${state.replaceAll(' ', '_')}.csv`)
  }
}

main(...process.argv.slice(2))
