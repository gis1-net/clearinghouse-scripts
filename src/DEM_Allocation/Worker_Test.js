const { workerData, parentPort } = require("worker_threads");

console.log(workerData.index)

parentPort.postMessage(workerData.index)