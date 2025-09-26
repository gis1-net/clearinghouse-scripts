const { workerData, parentPort } = require("worker_threads");
const sortDemFiles = require('./DEM_Sort.js')

sortDemFiles(workerData.state, workerData.county).then(data => parentPort.postMessage(data))