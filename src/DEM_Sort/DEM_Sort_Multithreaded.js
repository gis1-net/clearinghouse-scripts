const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { Worker } = require("worker_threads");

const jobs = []

const createWorker = async () => {
  while (jobs.length) {
    const job = jobs.shift()

    await new Promise((resolve, reject) => {
      const worker = new Worker("./Allocate_DEM_Files_Thread.js", {
        workerData: job,
      });
      worker.on("message", (res) => {
        resolve(res);
      });
      worker.on("error", (msg) => {
        reject(`An error ocurred: ${msg}`);
      });
    })
  }
}

const main = async (numThreads, state) => {
  const workerPromises = []

  const data = readJsonData(`DEM_Allocation/${state}.json`)

  for (let i = 0; i < data.length; i++) {
    jobs.push({ state, index: i, count: data.length })
  }

  for (let i = 0; i < numThreads; i++) {
    workerPromises.push(createWorker())
  }

  await Promise.all(workerPromises)
}

main(...process.argv.slice(2))