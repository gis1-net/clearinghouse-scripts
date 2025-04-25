const { workerData, parentPort } = require("worker_threads");
const sortDemFiles = require('./DEM_Sort.js')

const data = sortDemFiles(workerData.state, workerData.index, workerData.count)

parentPort.postMessage(data)