const generateUtmZoneBoundaries = require('./Generate_UTM_Zone_Boundaries')
const generateUtm10kIndexGrids = require('./Generate_UTM_10k_Index_Grids')
const reprojectUtm10kIndexGridsToShapefile = require('./Reproject_UTM_10k_Index_Grids_To_Shapefile')

const main = async () => {
  console.log('RUNNING GENERATE_UTM')
  await generateUtmZoneBoundaries()

  console.log('RUNNING GRID')
  await generateUtm10kIndexGrids()

  console.log('RUNNING REPROJECT')
  await reprojectUtm10kIndexGridsToShapefile()
}

main()