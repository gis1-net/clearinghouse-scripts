const { workerData, parentPort } = require("worker_threads");
const download = require('./DEM_Download_Tile')

download(workerData.url, workerData.path, workerData.i, workerData.count)

parentPort.postMessage(null)