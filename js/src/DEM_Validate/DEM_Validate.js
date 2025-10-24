const fs = require('fs')
const path = require('path')
const { fromFile } = require('geotiff')

// Validation constants
const MIN_ALLOWED = -400
const MAX_ALLOWED = 2600
const SAMPLE_GRID = 256

/**
 * Open a GeoTIFF file using geotiff.js with broad compatibility across versions.
 * @param {string} filePath
 * @returns {Promise<any>} GeoTIFF object
 */
async function openTiff(filePath) {
  // Wrap in try/catch so callers can differentiate file I/O vs parsing errors
  try {
    return await fromFile(filePath)
  } catch (err) {
    err.__stage = 'open'
    throw err
  }
}

/**
 * Try to detect a NoData value from image metadata/tags.
 * @param {any} image GeoTIFF Image
 * @returns {number|undefined}
 */
function detectNoData(image) {
  const nd = image.getGDALNoData()
  if (nd == null || nd === '') return undefined
  const v = Number(nd)
  return Number.isNaN(v) ? undefined : v
}

/**
 * Attempt to read min/max from metadata to avoid full scans.
 * Checks GDAL statistics and TIFF Min/Max tags if present.
 * @param {any} image
 * @returns {{min:number, max:number}|undefined}
 */
function detectMinMax(image) {
  const md = image.getGDALMetadata() || {}
  const statMin = md['STATISTICS_MINIMUM']
  const statMax = md['STATISTICS_MAXIMUM']
  if (statMin == null || statMax == null || statMin === '' || statMax === '') return undefined
  const min = Number(statMin)
  const max = Number(statMax)
  if (Number.isNaN(min) || Number.isNaN(max)) return undefined
  return { min, max }
}

/**
 * Downsampled scan across the full raster using geotiff.js resampling.
 * @param {any} image
 * @param {number} targetW max sample columns
 * @param {number} targetH max sample rows
 * @returns {{
 *   validCount: number,
 *   zeroCount: number,
 *   nanCount: number,
 *   oobCount: number,
 *   minObserved: number|null,
 *   maxObserved: number|null
 * }}
 */
async function sampleScan(image, targetW, targetH, minAllowed, maxAllowed, noDataValue) {
  const width = image.getWidth()
  const height = image.getHeight()

  const outW = Math.max(1, Math.min(width, targetW))
  const outH = Math.max(1, Math.min(height, targetH))

  let data
  try {
    data = await image.readRasters({
      window: [0, 0, width, height],
      width: outW,
      height: outH,
      samples: [0],
      interleave: true,
    })
  } catch (err) {
    // Reading failed (likely corrupt). Return a sentinel result indicating failure.
    return {
      readError: true,
      errorMessage: err && err.message ? err.message : String(err),
      validCount: 0,
      zeroCount: 0,
      nanCount: 0,
      oobCount: 0,
      nodataCount: 0,
      minObserved: null,
      maxObserved: null,
      outW,
      outH,
    }
  }

  let validCount = 0
  let zeroCount = 0
  let nanCount = 0
  let oobCount = 0
  let nodataCount = 0
  let minVal = Infinity
  let maxVal = -Infinity

  for (let i = 0; i < data.length; i++) {
    const v = data[i]

    if (noDataValue !== undefined && v === noDataValue) {
      nodataCount++
      continue
    }

    if (Number.isNaN(v)) {
      nanCount++
      continue
    }

    if (v === 0) {
      zeroCount++
      if (v < minVal) minVal = v
      if (v > maxVal) maxVal = v
      continue
    }

    validCount++
    if (v < minVal) minVal = v
    if (v > maxVal) maxVal = v
    if (v < minAllowed || v > maxAllowed) oobCount++
  }

  return {
    validCount,
    zeroCount,
    nanCount,
    oobCount,
    nodataCount,
    minObserved: Number.isFinite(minVal) ? minVal : null,
    maxObserved: Number.isFinite(maxVal) ? maxVal : null,
    outW,
    outH,
  }
}

/**
 * Validate a DEM GeoTIFF quickly using metadata and sampling:
 *  - Contains at least one valid pixel (not NoData, not NaN, not 0) within the sample grid
 *  - All sampled valid pixel values are within [-400, 2600]
 *  - If metadata min/max exist, they are also enforced to be within bounds
 *
 * @param {string} filePath path to .tif file
 * Uses MIN_ALLOWED, MAX_ALLOWED, SAMPLE_GRID constants for validation
 * @returns {Promise<{valid: boolean, summary: object, errors: string[]}>}
 */
async function validateGeoTIFF(filePath) {
  const minAllowed = MIN_ALLOWED
  const maxAllowed = MAX_ALLOWED
  const sampleGrid = SAMPLE_GRID

  if (!filePath) throw new Error('Missing file path')
  if (!fs.existsSync(filePath)) throw new Error(`File not found: ${filePath}`)

  let tiff, image
  try {
    tiff = await openTiff(filePath)
    image = await tiff.getImage()
  } catch (err) {
    return {
      valid: false,
      summary: { path: path.resolve(filePath) },
      errors: [
        `Failed to open or parse GeoTIFF: ${err && err.message ? err.message : String(err)}`,
      ],
    }
  }

  const width = image.getWidth()
  const height = image.getHeight()
  const samplesPerPixel = image.getSamplesPerPixel()

  let noDataValue
  let metaMinMax
  try {
    noDataValue = detectNoData(image)
    metaMinMax = detectMinMax(image)
  } catch (e) {
    // If metadata access throws (rare), continue with undefineds
  }

  // If metadata indicates out-of-bounds, note it
  let metadataOutOfBounds = false
  if (metaMinMax) {
    if (metaMinMax.min < minAllowed || metaMinMax.max > maxAllowed) {
      metadataOutOfBounds = true
    }
  }

  // Perform downsampled scan across entire raster
  const sampled = await sampleScan(
    image,
    sampleGrid,
    sampleGrid,
    minAllowed,
    maxAllowed,
    noDataValue
  )

  const errors = []

  if (sampled.readError) {
    errors.push(`Raster read failed (likely corrupt): ${sampled.errorMessage}`)
  } else {
    // Must have at least one non-zero, non-NoData pixel in the sample
    if (sampled.validCount === 0) {
      errors.push('No valid sampled pixels found (all NoData/NaN/0 in sample).')
    }

    // Zero values are considered invalid by requirement
    if (sampled.zeroCount > 0) {
      errors.push(`Found ${sampled.zeroCount.toLocaleString()} zero-valued pixels among sampled non-NoData values.`)
    }

    // Enforce bounds: metadata and sampled values
    if (metadataOutOfBounds) {
      errors.push(`Metadata min/max outside bounds [${minAllowed}, ${maxAllowed}] (min=${metaMinMax.min}, max=${metaMinMax.max}).`)
    }
    if (sampled.oobCount > 0) {
      errors.push(`Found ${sampled.oobCount.toLocaleString()} sampled pixel values outside bounds [${minAllowed}, ${maxAllowed}].`)
    }
  }

  const summary = {
    path: path.resolve(filePath),
    width,
    height,
    samplesPerPixel,
    sampleGridUsed: { width: sampled.outW, height: sampled.outH },
    noDataValue: Number.isFinite(noDataValue) ? noDataValue : undefined,
    metadataMin: metaMinMax ? metaMinMax.min : undefined,
    metadataMax: metaMinMax ? metaMinMax.max : undefined,
    validSampleCount: sampled.validCount,
    zeroSampleCount: sampled.zeroCount,
    nanSampleCount: sampled.nanCount,
    noDataSampleCount: sampled.nodataCount,
    outOfBoundsSampleCount: sampled.oobCount,
    minObservedSample: sampled.minObserved,
    maxObservedSample: sampled.maxObserved,
    allowedRange: [minAllowed, maxAllowed],
    readError: !!sampled.readError,
  }

  // If any read/parsing error or validation issue: invalid
  return { valid: errors.length === 0, summary, errors }
}

const main = async (filePath) => {
  try {
    const { valid, summary, errors } = await validateGeoTIFF(filePath)

    // Reduce output to a simple corrupt/not-corrupt verdict, but keep minimal context.
    if (valid) {
      console.log(`[${filePath}] Successfully validated`)
      // console.log('CORRUPT: false')
      // console.log(JSON.stringify({ path: summary.path, width: summary.width, height: summary.height }, null, 2))
      return 0
    } else {
      console.log(`[${filePath}] CORRUPTION DETECTED`)
      // if (errors && errors.length) {
      //   console.log('Reason:')
      //   for (const e of errors) console.log(`- ${e}`)
      // }
      return 1
    }
  } catch (err) {
    // Any unhandled error is treated as corrupt with reason
    console.log('CORRUPT: true')
    console.log('Reason:')
    console.log(`- ${err && err.message ? err.message : String(err)}`)
    return 2
  }
}

if (require.main === module) {
  const [filePath] = process.argv.slice(2)
  if (!filePath) {
    console.error('Usage: node DEM_Validate.js <path-to-file.tif>')
    process.exit(2)
  }
  main(filePath).then(code => process.exit(code))
}

module.exports = { main, validateGeoTIFF }