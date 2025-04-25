const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { groupBy } = require('lodash')
const { Worker } = require("worker_threads");
const ObjectsToCsv = require('objects-to-csv');
const fs = require('fs')

const projects = readJsonData('Lidar_Project_Boundaries.geojson')

const jobs = []
const data = []

const createWorker = async () => {
  while (jobs.length) {
    const job = jobs.shift()

    const response = await new Promise((resolve, reject) => {
      const worker = new Worker("./Generate_Lidar_Project_Grids_Thread.js", {
        workerData: job,
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

const main = async (numThreads) => {
  const workerPromises = []

  const targetProjects = projects.features.filter(f => fs.existsSync(`../../data/DEM_Download_Lists/${f.properties.workunit}.txt`))

  for (let i = 0; i < targetProjects.length; i++) {
    const project = targetProjects[i]

    jobs.push({ 
      project: project.properties.workunit,
      i,
      count: targetProjects.length
    })
  }

  for (let i = 0; i < numThreads; i++) {
    workerPromises.push(createWorker(i))
  }

  await Promise.all(workerPromises)
}

main(...process.argv.slice(2))