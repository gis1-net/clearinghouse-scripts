const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { fromUrl, fromArrayBuffer, fromBlob  } = require("geotiff");
const proj4 = require("proj4");
const { addDefs } = require("#data/Coordinate_Systems/proj4_defs.js")
const geokeysToProj4 = require("geotiff-geokeys-to-proj4");
const fs = require('fs')
const coordinateSystemDetails = readJsonData('Coordinate_Systems/coordinate_system_details.json')

addDefs(proj4)

const main = async (project, i = 0, count = 1) => {
  console.log(`(${parseInt(i) + 1}/${count}) Building grid for ${project}...`)
  const contents = fs.readFileSync(`../../data/DEM_Download_Lists/${project}.txt`, 'utf-8')

  const urls = contents.split('\n')

  const features = []

  for (let url of urls) {
    console.log(`Fetching Tile Info From ${url}`)

    if (!url) {
      continue
    }

    let retry = 10
    while (retry-- > 0) {
      try {
        const tileName = url.split('/').pop().split('.').shift()
        const tiff = await fromUrl(url)
        const image = await tiff.getImage()

        const boundingBox = image.getBoundingBox()
        const geoKeys = image.getGeoKeys()
        const projObj = geokeysToProj4.toProj4(geoKeys);
        // const projection = proj4(projObj.proj4, "WGS84");

        let crsName = geoKeys.GTCitationGeoKey

        if (crsName === 'unnamed') {
          crsName = 'WGS84'
        }

        // if (project === 'VA_Shenandoah_2014' || project === 'VA_Shen_Multi_Haz_2014') {
        //   crsName = 'WGS84'
        // }

        console.log(`\n\nCRS NAME: ${crsName}\n\n`)

        let crsDetails = coordinateSystemDetails.find(crs => crs.name === crsName)

        if (!crsDetails) {
          crsDetails = coordinateSystemDetails.find(crs => crs.name === crsName.split(' + ')[0])
        }
        if (!crsDetails) {
          crsDetails = coordinateSystemDetails.find(crs => crs.name.replaceAll('(2011)', '') === crsName.replaceAll('(2011)', ''))
        }
        if (!crsDetails) {
          crsDetails = coordinateSystemDetails.find(crs => crs.name.replaceAll('(2011)', '').replaceAll(' / ', ' ').replaceAll('(', '').replaceAll(')', '').replaceAll('_', ' ') === crsName.replaceAll('(2011)', '').replaceAll(' / ', ' ').replaceAll('(', '').replaceAll(')', '').replaceAll('_', ' '))
        }
        if (!crsDetails) {
          const searchName = crsName
            .split('=')
            .pop()
            .trim()
            .replaceAll('_', ' ')
            .replaceAll('(', '')
            .replaceAll(')', '')
            .replaceAll('1983', '')
            .replaceAll('2011', '')
            .replaceAll('/', ' ')
            .replaceAll(/\s+/g, ' ')
            .toLowerCase()
            .replaceAll('nad83', 'nad')

          console.log(`\n\nSEARCH NAME: ${searchName}\n\n`)

          crsDetails = coordinateSystemDetails.find(crs => {
            const csName = crs.name
              .split('=')
              .pop()
              .trim()
              .replaceAll('_', ' ')
              .replaceAll('(', '')
              .replaceAll(')', '')
              .replaceAll('1983', '')
              .replaceAll('2011', '')
              .replaceAll('/', ' ')
              .replaceAll(/\s+/g, ' ')
              .toLowerCase()
              .replaceAll('nad83', 'nad')
            return csName === searchName
          })
        }

	      let proj4Key = ''

        if (crsName === 'WGS84') {
          proj4Key = 'WGS84'
        } else if (!crsDetails) {
          console.log(geoKeys)
          throw new Error(`Coordinate System ${crsName} not found`)
        } else {
          proj4Key = `${crsDetails.id.authority}:${crsDetails.id.code}`
        }

        const projection = proj4(proj4Key)

        const maxX = Math.max(boundingBox[0], boundingBox[2])
        const minX = Math.min(boundingBox[0], boundingBox[2])
        const maxY = Math.max(boundingBox[1], boundingBox[3])
        const minY = Math.min(boundingBox[1], boundingBox[3])

        console.log(boundingBox, projObj)

        const corner1 = projection.inverse([maxX, maxY])
        const corner2 = projection.inverse([minX, maxY])
        const corner3 = projection.inverse([minX, minY])
        const corner4 = projection.inverse([maxX, minY])

        const feature = {
          type: "Feature",
          properties: {
            TILE_NAME: tileName
          },
          geometry: {
            type: 'Polygon',
            coordinates: [
              [
                corner1,
                corner2,
                corner3,
                corner4,
                corner1
              ]
            ]
          }
        }

        features.push(feature)

        retry = 0
      } catch (error) {
        console.log(`Failed to create tile for ${url}`)
        throw error
      }
    }
  }

  writeJsonData(`Lidar_Project_Grids/${project}.geojson`, { type: 'FeatureCollection', features })
}

if (require.main === module) {
  main(...process.argv.slice(2))
}

module.exports = main
