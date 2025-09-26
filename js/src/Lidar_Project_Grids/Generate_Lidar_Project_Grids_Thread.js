const { workerData, parentPort } = require("worker_threads");
const generate = require('./Generate_Lidar_Project_Grids')

generate(workerData.project, workerData.i, workerData.count).then(res => parentPort.postMessage(res))