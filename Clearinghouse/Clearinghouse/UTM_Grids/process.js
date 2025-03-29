const generateUtm = require('./generate_utm')
const grid = require('./grid')
const reproject = require('./reproject')

const main = async () => {
  console.log('RUNNING GENERATE_UTM')
  await generateUtm()

  console.log('RUNNING GRID')
  await grid()

  console.log('RUNNING REPROJECT')
  await reproject()
}

main()