const fs = require('fs')

const url = "https://index.nationalmap.gov/arcgis/rest/services/3DEPElevationIndex/MapServer/24/query?&f=json&returnTrueCurves=false&spatialRel=esriSpatialRelIntersects&inSR=3857&outSR=3857&outfields=*&geometry=%7B%22xmin%22:{XMIN},%22ymin%22:{YMIN},%22xmax%22:{XMAX},%22ymax%22:{YMAX},%22spatialReference%22:%7B%22wkid%22:4326%7D%7D&geometryType=esriGeometryEnvelope"
// https://index.nationalmap.gov/arcgis/rest/services/3DEPElevationIndex/MapServer/24/query?&f=json&returnTrueCurves=false&spatialRel=esriSpatialRelIntersects&inSR=3857&outSR=3857&outfields=*&geometry=%7B%22xmin%22:-126.25216369974582,%22ymin%22:24.623944605264953,%22xmax%22:-65.70196687602497,%22ymax%22:50.09582090190062,%22spatialReference%22:%7B%22wkid%22:4326%7D%7D&geometryType=esriGeometryEnvelope

const main = async () => {
  const xStart = -198.14125134417745
  const yStart = 10.954241520156486
  const xEnd = -64.324712133489
  const yEnd = 72.97689246650987

  const xSlices = 20
  const ySlices = 20
  const xDelta = (xEnd - xStart) / xSlices
  const yDelta = (yEnd - yStart) / ySlices

  const features = []
  
  for (let i = 0; i < xSlices; i++) {
    for (let j = 0; j < ySlices; j++) {
      console.log(`Fetching slice ${i}, ${j}`)
      let retry = 3

      while (retry > 0) {
        const xMin = xStart + i * xDelta
        const xMax = xMin + xDelta
        const yMin = yStart + j * yDelta
        const yMax = yMin + yDelta

        const queryUrl = url.replace("{XMIN}", xMin).replace("{XMAX}", xMax).replace("{YMIN}", yMin).replace("{YMAX}", yMax)

        const response = await fetch(queryUrl)
        const data = await response.json()

        if (data.exceededTransferLimit) {
          console.log("Exceeded transfer limit, retrying")
          retry--
        } else if (!data.features) {
          console.log("No features, retrying")
          retry--
        } else {
          retry = -1
        }
        
        features.push(...data.features)
      }

      if (retry === 0) {
        throw new Error("Failed to fetch data")
      }
    }
  }
  
  console.log('Writing to file: ', features.length)
  fs.writeFileSync("project_features_raw.json", JSON.stringify(features))
}

main()