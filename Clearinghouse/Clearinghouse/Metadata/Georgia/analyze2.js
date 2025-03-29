const countyProjects = require('../../LidarProjects/County_Projects.json')
const { groupBy } = require('lodash')
const usgsProjects = require('../../LidarProjects/USGS_Projects.json')
const fs = require('fs')
const usCounties = require('../../LidarProjects/US_Counties.json')
const turf = require('@turf/turf')
const ObjectsToCsv = require('objects-to-csv');
const { readCSVSync } = require('read-csv-sync');

const main = async () => {
  const gaMetadata = readCSVSync('./Georgia_Counties_Metadata.csv')
  gaMetadata.pop()

  const gaProjects = countyProjects.filter(p => p.state === 'Georgia' && ['QL 2', 'QL 1', 'QL 0'].includes(p.ql))

  const gaCountyProjects = groupBy(gaProjects, 'county')

  const newMetadata = []

  for (let countyMetadata of gaMetadata) {
    const newCountyMetadata = { ...countyMetadata }
    const start = countyMetadata.collection.split('-')

    const startMonth = start[0]
    const startYear = start[1]

    const end = countyMetadata.collecti_1.split('-')

    const endMonth = end[0]
    const endYear = end[1]

    const projects = gaCountyProjects[countyMetadata.county]

    const startMatchProjects = projects.filter(p => {
      const startDate = new Date(p.collect_start)
      return ((startDate.getMonth() + 1) == startMonth) && ((startDate.getYear() + 1900) == startYear)
    })

    const endMatchProjects = projects.filter(p => {
      const endDate = new Date(p.collect_end)
      return ((endDate.getMonth() + 1) == endMonth) && ((endDate.getYear() + 1900) == endYear)
    })

    const exactMatchProjects = projects.filter(p => {
      const startDate = new Date(p.collect_start)
      const endDate = new Date(p.collect_end)
      return ((startDate.getMonth() + 1) == startMonth) && ((startDate.getYear() + 1900) == startYear) && ((endDate.getMonth() + 1) == endMonth) && ((endDate.getYear() + 1900) == endYear)
    })

    if (exactMatchProjects.length === 1) {
      newCountyMetadata.needs_revi = false
      newCountyMetadata.projects = exactMatchProjects[0].workunit
    } else {
      newCountyMetadata.needs_revi = true
      newCountyMetadata.projects = ''
    }

    newMetadata.push(newCountyMetadata)
  }

  const csv = new ObjectsToCsv(newMetadata)
  await csv.toDisk('./Georgia_Counties_Metadata_2.csv')
}

main()