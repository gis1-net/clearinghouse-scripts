const { workerData, parentPort } = require("worker_threads");
const verify = require('./Verify_Lidar_Project_Grids')

verify(workerData.project, workerData.i, workerData.count).then(res => parentPort.postMessage(res))
