const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { groupBy } = require('lodash')
const { Worker } = require("worker_threads");
const ObjectsToCsv = require('objects-to-csv');
const fs = require('fs')

const jobs = []

const createWorker = async () => {
  while (jobs.length) {
    const job = jobs.shift()

    let response = false

    while (!response) {
      try {
        response = await new Promise((resolve, reject) => {
            const worker = new Worker(`${__dirname}/DEM_Download_Thread.js`, {
              workerData: job,
            });
            worker.on("message", (res) => {
              resolve(res);
            });
            worker.on("error", (res) => {
              reject(res);
            });
        })
      } catch (error) {
        console.log('CAUGHT ERROR, RETRYING', error)
      }
    }
  }
}

const main = async (numThreads, state) => {
  const workerPromises = []

  const demAllocations = readJsonData(`DEM_Allocation/${state.replaceAll(' ', '_')}.json`)

  const stateProjects = new Set()
  const missingProjects = new Set()

  for (let county of demAllocations) {
    if (county.projects_1) {
      const countyProjects = county.projects_1.split('|')
      for (let project of countyProjects) {
        if (fs.existsSync(`${__dirname}/../../data/DEM_Download_Lists/${project}.txt`)) {
          stateProjects.add(project)
        } else {
          missingProjects.add(project)
        }
      }
    }
  }

  const downloadUrls = new Set()

  console.log('Building download list...')

  for (let project of stateProjects) {
    if (fs.readdirSync(`/mnt/z/${state.toUpperCase().replaceAll(' ', '_')}/Tif_Files_UTM/${project}/`).length < 10) {
      fs.rmSync(`/mnt/z/${state.toUpperCase().replaceAll(' ', '_')}/Tif_Files_UTM/${project}/`, { recursive: true })

      fs.mkdirSync(`/mnt/z/${state.toUpperCase().replaceAll(' ', '_')}/Tif_Files_UTM/${project}/`)
    }

    if (!fs.existsSync(`/mnt/z/${state.toUpperCase().replaceAll(' ', '_')}/Tif_Files_UTM/${project}/`)) {
      fs.mkdirSync(`/mnt/z/${state.toUpperCase().replaceAll(' ', '_')}/Tif_Files_UTM/${project}/`, { recursive: true })
    }

    const file = fs.readFileSync(`${__dirname}/../../data/DEM_Download_Lists/${project}.txt`, 'utf-8')
    const lines = file.split('\n')

    for (let line of lines) {
     if (line) {
        downloadUrls.add({ url: line, project })
     }
    }
  }

  const downloads = Array.from(downloadUrls)

  for (let i = 0; i < downloads.length; i++) {
    const download = downloads[i]

    const fileName = download.url.split('/').pop()

    jobs.push({ 
      url: download.url, 
      path: `/mnt/z/${state.toUpperCase().replaceAll(' ', '_')}/Tif_Files_UTM/${download.project}/${fileName}`,
      i,
      count: downloads.length
    })
  }

  console.log(`Found ${downloads.length} urls to download. Starting on ${numThreads} threads.`)

  for (let i = 0; i < numThreads; i++) {
    workerPromises.push(createWorker(i))
  }

  await Promise.all(workerPromises)
}

main(...process.argv.slice(2))
