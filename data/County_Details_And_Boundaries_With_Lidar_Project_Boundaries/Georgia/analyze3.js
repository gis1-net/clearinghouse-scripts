const countyProjects = require('../../LidarProjects/County_Projects_New.json')
const { groupBy } = require('lodash')
const usgsProjects = require('../../LidarProjects/USGS_Projects.json')
const fs = require('fs')
const usCounties = require('../../LidarProjects/US_Counties.json')
const turf = require('@turf/turf')
const ObjectsToCsv = require('objects-to-csv');
const { readCSVSync } = require('read-csv-sync');

const main = async () => {
  const gaMetadata = readCSVSync('./Georgia_Counties_Metadata_3.csv')
  gaMetadata.pop()

  const gaProjects = countyProjects.filter(p => p.state === 'Georgia' && ['QL 2', 'QL 1', 'QL 0'].includes(p.ql))

  const gaCountyProjects = groupBy(gaProjects, 'county')

  const newMetadata = []

  for (let countyMetadata of gaMetadata) {
    const projects = countyMetadata.projects.split('|')

    let start = Number.MAX_SAFE_INTEGER
    let end = 0

    const errors = []

    for (let project of projects) {
      const lidarProject = gaCountyProjects[countyMetadata.county].find(p => p.workunit === project)

      if (lidarProject) {
        start = Math.min(start, lidarProject.collect_start)
        end = Math.max(end, lidarProject.collect_end)
      } else {
        console.log(`Could not find project ${project} for county ${countyMetadata.county}`)
        errors.push('UNKNOWN_PROJECT')
      }
    }

    const startDate = new Date(start)
    const endDate = new Date(end)

    const startMonth = startDate.getMonth() + 1
    const startYear = startDate.getFullYear()

    const endMonth = endDate.getMonth() + 1
    const endYear = endDate.getFullYear()

    const metadataStart = countyMetadata.start.split('-')
    const metadataEnd = countyMetadata.end.split('-')

    if (startMonth !== parseInt(metadataStart[0]) || startYear !== parseInt(metadataStart[1])) {
      console.log(`Start date does not match for ${countyMetadata.county}`)
      errors.push('MISMATCH_START')
    }

    if (endMonth !== parseInt(metadataEnd[0]) || endYear !== parseInt(metadataEnd[1])) {
      console.log(`End date does not match for ${countyMetadata.county}`)
      errors.push('MISMATCH_END')
    }

    newMetadata.push({
      ...countyMetadata,
      needs_revi: errors.length > 0,
      errors: errors.join('|')
    })
  }

  const csv = new ObjectsToCsv(newMetadata)
  await csv.toDisk('./Georgia_Counties_Metadata_4.csv')
}

main()