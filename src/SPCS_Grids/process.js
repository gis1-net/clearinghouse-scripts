const join = require('./join')
const union = require('./union')
const grid = require('./grid')
const reproject = require('./reproject')

const main = async () => {
  // console.log('RUNNING JOIN')
  // await join()

  // console.log('RUNNING UNION')
  // await union()

  console.log('RUNNING GRID')
  await grid()

  console.log('RUNNING REPROJECT')
  await reproject()
}

main()