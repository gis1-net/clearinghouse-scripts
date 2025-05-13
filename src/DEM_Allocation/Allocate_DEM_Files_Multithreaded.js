const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { groupBy } = require('lodash')
const { Worker } = require("worker_threads");
const counties = readJsonData('US_County_Details_And_Boundaries.geojson')
const ObjectsToCsv = require('objects-to-csv');

const jobs = []
const data = []

const createWorker = async () => {
  while (jobs.length) {
    const job = jobs.shift()

    const response = await new Promise((resolve, reject) => {
      const worker = new Worker("./Allocate_DEM_Files_Thread.js", {
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

  for (let state in stateGroups) {
    writeJsonData(`DEM_Allocation/${state.replaceAll(' ', '_')}.json`, stateGroups[state])

    const csvData = []

    for (let county of stateGroups[state]) {
      for (let group of county.groups) {
        csvData.push({
          name: county.name,
          lsad: county.lsad,
          state: county.state,
          projects: group.join('|')
        })
      }
    }

    console.log(`Writing DEM_Allocation/${state.replaceAll(' ', '_')}.csv`)
    const csv = new ObjectsToCsv(csvData)
    await csv.toDisk(`../../data/DEM_Allocation/${state.replaceAll(' ', '_')}.csv`)
  }
}

main(...process.argv.slice(2))
