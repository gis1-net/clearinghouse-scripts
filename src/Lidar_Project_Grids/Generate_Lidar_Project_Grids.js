const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const { fromUrl, fromArrayBuffer, fromBlob  } = require("geotiff");
const proj4 = require("proj4");
const geokeysToProj4 = require("geotiff-geokeys-to-proj4");
const fs = require('fs')

const main = async (project, i = 0, count = 1) => {
  console.log(`(${i + 1}/${count}) Building grid for ${project}...`)
  const contents = fs.readFileSync(`../../data/DEM_Download_Lists/${project}.txt`, 'utf-8')
  
  const urls = contents.split('\n')

  const features = []

  for (let url of urls) {
    // console.log(`Fetching Tile Info From ${url}`)

    try {
      const tileName = url.split('/').pop().split('.').shift()
      const tiff = await fromUrl(url)
      const image = await tiff.getImage()

      const boundingBox = image.getBoundingBox()
      const geoKeys = image.getGeoKeys()
      const projObj = geokeysToProj4.toProj4(geoKeys);
      const projection = proj4(projObj.proj4, "WGS84");

      const maxX = Math.max(boundingBox[0], boundingBox[2])
      const minX = Math.min(boundingBox[0], boundingBox[2])
      const maxY = Math.max(boundingBox[1], boundingBox[3])
      const minY = Math.min(boundingBox[1], boundingBox[3])

      const corner1 = projection.forward([maxX, maxY])
      const corner2 = projection.forward([minX, maxY])
      const corner3 = projection.forward([minX, minY])
      const corner4 = projection.forward([maxX, minY])

      const feature = {
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
    } catch (error) {
      console.log(`Failed to create tile for ${url}`)
    }
  }

  writeJsonData(`Lidar_Project_Grids/${project}.geojson`, { type: 'FeatureCollection', features })
}

if (require.main === module) {
  main(...process.argv.slice(2))
}

module.exports = main