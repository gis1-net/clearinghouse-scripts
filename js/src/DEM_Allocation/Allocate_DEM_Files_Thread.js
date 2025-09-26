const { workerData, parentPort } = require("worker_threads");
const allocateDemFiles = require('./Allocate_DEM_Files')

const data = allocateDemFiles(workerData.index, false)

parentPort.postMessage(data)