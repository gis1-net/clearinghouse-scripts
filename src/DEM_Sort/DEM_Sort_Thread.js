const { workerData, parentPort } = require("worker_threads");
const sortDemFiles = require('./DEM_Sort.js')

const data = sortDemFiles(workerData.index, workerData.stateFolder)

parentPort.postMessage(data)