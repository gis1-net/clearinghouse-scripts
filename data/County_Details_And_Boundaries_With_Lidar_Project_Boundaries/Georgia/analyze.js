const countyProjects = require('../../LidarProjects/County_Projects_New.json')
const { groupBy } = require('lodash')
const usgsProjects = require('../../LidarProjects/USGS_Projects.json')
const fs = require('fs')
const usCounties = require('../../LidarProjects/US_Counties.json')
const turf = require('@turf/turf')
const ObjectsToCsv = require('objects-to-csv');

const main = async () => {
  const gaProjects = countyProjects.filter(p => p.state === 'Georgia' && ['QL 2', 'QL 1', 'QL 0'].includes(p.ql))

  const gaCountyProjects = groupBy(gaProjects, 'county')

  // console.log(gaCountyProjects['Baker'].map(p => p.project))
  // return

  const countyCollectDates = {}
  const countyMetadata = []

  for (let county in gaCountyProjects) {
    let output = { start: Number.MAX_SAFE_INTEGER, end: 0 }

    const countyGeometry = usCounties.features.find(c => c.properties.STATE === 'Georgia' && c.properties.NAME === county)
    let projectGeometry = null

    const projects = []

    for (let project of gaCountyProjects[county]) {
      projects.push(project.workunit)
      const usgsProject = usgsProjects.features.find(p => p.properties.workunit === project.workunit)

      if (projectGeometry) {
        projectGeometry = turf.union(turf.featureCollection([projectGeometry, usgsProject]))
      } else {
        projectGeometry = usgsProject
      }

      const coversCounty = turf.booleanEqual(countyGeometry.geometry, turf.intersect(turf.featureCollection([projectGeometry, countyGeometry])).geometry)

      output = { 
        start: Math.min(project.collect_start, output.start), 
        end: Math.max(project.collect_end, output.end)
      }

      if (coversCounty) {
        break;
      }
    }

    countyCollectDates[county] = {
      start: new Date(output.start),
      end: new Date(output.end),
      projects
    }
  }

  const inspectCounties = {}

  for (let county in countyCollectDates) {
    const { start, end, projects } = countyCollectDates[county]

    const startMonth = start.getMonth() + 1
    const startYear = start.getYear() + 1900

    const endMonth = end.getMonth() + 1
    const endYear = end.getYear() + 1900

    const metadata = { county, collection_start: `${startMonth}-${startYear}`, collection_end: `${endMonth}-${endYear}`, projects: projects.join(', ') }

    if (endYear - startYear > 3) {
      inspectCounties[county] = {
        start: `${startMonth}-${startYear}`,
        end: `${endMonth}-${endYear}`
      }

      metadata.needs_review = true
    } else {
      metadata.needs_review = false
    }

    countyCollectDates[county] = {
      start: `${startMonth}-${startYear}`,
      end: `${endMonth}-${endYear}`
    }

    countyMetadata.push(metadata)
  }

  for (county in countyCollectDates) {
    const features = gaCountyProjects[county].map(p => usgsProjects.features.find(f => f.properties.workunit === p.workunit))
    const countyFeature = usCounties.features.find(f => f.properties.STATE === 'Georgia' && f.properties.NAME === county)
    fs.writeFileSync(`./${county}.geojson`, JSON.stringify({ type: 'FeatureCollection', features: [...features, countyFeature] }, null, 2))
  }

  const csv = new ObjectsToCsv(countyMetadata)
  await csv.toDisk('./Georgia_Counties_Metadata.csv')
}

main()