const { workerData, parentPort } = require("worker_threads");
const download = require('./DEM_Download')

download(workerData.url, workerData.path, workerData.i, workerData.count).then(res => parentPort.postMessage(res))
