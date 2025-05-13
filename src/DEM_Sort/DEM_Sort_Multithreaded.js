const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { Worker } = require("worker_threads");
const { readCSVSync } = require("read-csv-sync")

const jobs = []

const createWorker = async () => {
  while (jobs.length) {
    const job = jobs.shift()

    await new Promise((resolve, reject) => {
      const worker = new Worker("./DEM_Sort_Thread.js", {
        workerData: job,
      });
      worker.on("message", (res) => {
        resolve(res);
      });
      worker.on("error", (event) => {
        console.log(event.stack)
        reject(`An error ocurred: ${event}`);
      });
    })
  }
}

const main = async (numThreads, state) => {
  const workerPromises = []

  const data = readCSVSync(`../../data/DEM_Allocation/${state}.csv`)

  for (let i = 0; i < data.length; i++) {
    if (data[i].name) {
      jobs.push({ state, index: i, count: data.length })
    }
  }

  for (let i = 0; i < numThreads; i++) {
    workerPromises.push(createWorker())
  }

  await Promise.all(workerPromises)
}

main(...process.argv.slice(2))
