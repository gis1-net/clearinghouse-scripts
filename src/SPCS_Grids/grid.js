const spcsZones = require('#data/SPCS_Zones.json')
const proj4 = require('proj4')
const { addDefs } = require('#data/Coordinate_Systems/defs.js')
const { keyBy } = require('lodash')
const turf = require('@turf/turf')
const fs = require('fs')
const states = require('#data/US_States.json')
const { FloodFiller, CELL_STATE } = require('./FloodFiller.js')

addDefs(proj4)

const main = async () => {
  const statesKeyed = keyBy(states, 'name')
  
  for (const spcsZone of spcsZones.features) {
    // if (!spcsZone.properties.SP_ZONE.startsWith('GEORGIA WEST')) {
    //   continue
    // }
    const stateAbr = statesKeyed[spcsZone.properties.STATE].abbreviation
    const zoneArea = spcsZone.properties.SP_ZONE.replace(spcsZone.properties.STATE.toUpperCase(), '').trim()
    const zoneAbr = zoneArea.split(' ').map(word => word[0]).join('')
    const prefix = `${stateAbr}${zoneAbr}`.toUpperCase()

    const polygon = spcsZone.geometry.type === 'MultiPolygon' ? turf.multiPolygon(spcsZone.geometry.coordinates) : turf.polygon(spcsZone.geometry.coordinates)
    const buffer = turf.buffer(polygon, 15000, { units: 'feet' })
    const envelope = turf.envelope(buffer)

    const csKey = spcsZone.properties.SPCS_AUTH + ':' + spcsZone.properties.SPCS_ID
    const spEnvelope = envelope.geometry.coordinates[0].map(coords => proj4(csKey).forward(coords))
    const spBbox = turf.bbox(turf.polygon([spEnvelope]))
    
    const origin = {
      x: Math.floor(spBbox[0] / 5000) * 5000,
      y: Math.floor(spBbox[1] / 5000) * 5000
    }

    const extent = {
      x: Math.ceil(spBbox[2] / 5000) * 5000,
      y: Math.ceil(spBbox[3] / 5000) * 5000
    }

    const xCount = Math.ceil((extent.x - origin.x) / 5000)
    const yCount = Math.ceil((extent.y - origin.y) / 5000)

    console.log(`Creating ${xCount}x${yCount} grid for ${prefix}`)

    await new Promise(resolve => {
      setTimeout(() => {
        resolve()
      }, 2000)
    })

    const gridTiles = []
    const grid = []

    let i = -1
    for (let x = origin.x; x < spBbox[2]; x += 5000) {
      const row = []
      i++
      let j = 0
      for (let y = origin.y; y < spBbox[3]; y += 5000) {
        console.log(`${i}/${xCount}, ${j++}/${yCount}`)
        const tile = {
          type: 'Feature',
          properties: {
            TILE_NUM: `${prefix}_${x.toString().substring(0, 4)}${y.toString().substring(0, 4)}`
          },
          geometry: {
            type: 'Polygon',
            coordinates: [[
              proj4(csKey).inverse([x, y]),
              proj4(csKey).inverse([x + 5000, y]),
              proj4(csKey).inverse([x + 5000, y + 5000]),
              proj4(csKey).inverse([x, y + 5000]),
              proj4(csKey).inverse([x, y])
            ]]
          }
        }

        const intersect = turf.booleanIntersects(turf.feature(tile).geometry, turf.feature(buffer).geometry)

        if (intersect) {
          gridTiles.push(tile)
          row.push(CELL_STATE.FILL)
        } else {
          row.push(undefined)
        }
      }

      grid.push(row)
    }

    const floodFiller = new FloodFiller(grid)
    const holes = floodFiller.findHoles()

    for (const hole of holes) {
      const [ i, j ] = hole
      console.log(`Filling hole (${i}, ${j})`)
      const x = origin.x + (i * 5000)
      const y = origin.y + (j * 5000)

      const tile = {
        type: 'Feature',
        properties: {
          TILE_NUM: `${prefix}_${x.toString().substring(0, 4)}${y.toString().substring(0, 4)}`
        },
        geometry: {
          type: 'Polygon',
          coordinates: [[
            proj4(csKey).inverse([x, y]),
            proj4(csKey).inverse([x + 5000, y]),
            proj4(csKey).inverse([x + 5000, y + 5000]),
            proj4(csKey).inverse([x, y + 5000]),
            proj4(csKey).inverse([x, y])
          ]]
        }
      }

      gridTiles.push(tile)
    }

    if (!fs.existsSync(`./SPCS_Grids_RAW/${spcsZone.properties.STATE}`)) {
      fs.mkdirSync(`./SPCS_Grids_RAW/${spcsZone.properties.STATE}`)
    }

    console.log(`Writing ${gridTiles.length} tiles for ${spcsZone.properties.SP_ZONE}, ${spcsZone.properties.STATE}`)
    const writeStream = fs.createWriteStream(`./SPCS_Grids_RAW/${spcsZone.properties.STATE}/${spcsZone.properties.SP_ZONE.replaceAll(' ', '_')}_Grid.geojson`)
    writeStream.write("{ \"type\": \"FeatureCollection\", \"features\": [\n")
    for (let i in gridTiles) {
      const tile = gridTiles[i]
      writeStream.write(JSON.stringify(tile))

      if (i != (gridTiles.length - 1)) {
        writeStream.write(',')
      }
      writeStream.write('\n')
    }
    writeStream.write(']\n}')
    writeStream.close()
  }
}

if (require.main === module) {
  main()
}

module.exports = main