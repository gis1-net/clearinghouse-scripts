const { readJsonData, writeJsonData } = require('#src/Utils/JSON_Data.js')
const turf = require('@turf/turf')
const { keyBy, orderBy } = require('lodash')
const { buildCombos, isStrictSuperset, dedupeSupersets } = require('./Combo_Builder')
const { analyzeCoverage } = require('./Coverage_Analyzer')

const counties = readJsonData('US_County_Details_And_Boundaries.geojson')
const usgs1mProjects = readJsonData('USGS_1m_Projects_List.json')

/** Minimum year for data to be considered "recent" - recent data is preferred over old data */
const RECENT_MIN_YEAR = 1970

/** Minimum fraction of the county's area that must be covered by a recent project for that project to be automatically used */
const RECENT_AUTOMATIC_USE_MINIMUM_COVERAGE = 0.1

/** Minimum fraction of the county's area that must be covered to consider full coverage */
const FULL_COVERAGE_MINIMUM = 0.999

/** Minimum fraction of the county's area that must be covered to consider the project significant for metadata purposes */
const SIGNIFICANT_COVERAGE_MINIMUM = 0.05

/** Maximum age gap between two projects to consider combining them into a single set of tiles */
const MAXIMUM_COMBINABLE_AGE_GAP_DAYS = 365 / 2

const main = (index, silent = false) => {
  const county = counties.features[index]

  console.log(`(${index}/3143) Checking ${county.properties.NAME} ${county.properties.LSAD}, ${county.properties.STATE}`)

  const countyProjects = keyBy(
    orderBy(
      readJsonData(`Lidar_Project_Boundaries_By_County/${county.properties.STATE}/${county.properties.NAME}_${county.properties.LSAD}_Lidar_Project_Boundaries.geojson`).features,
      p => p.properties.collect_end,
      'desc'
    ),
    p => p.properties.workunit
  )

  const candidateProjects = []

  /** Find recent projects that meet the minimum threshold for automatic usage */
  for (let key in countyProjects) {
    const countyProject = countyProjects[key]

    const coverage = analyzeCoverage(county, countyProject)

    const endDate = new Date(countyProject.properties.collect_end)

    if (endDate.getFullYear() >= RECENT_MIN_YEAR && coverage >= RECENT_AUTOMATIC_USE_MINIMUM_COVERAGE && ['QL 0', 'QL 1', 'QL 2'].includes(countyProject.properties.ql)) {
      candidateProjects.push({ project: countyProject, coverage })
    }
  }

  /** Build the list of every possible unique combination of projects */
  const combos = buildCombos(candidateProjects)

  /** Looks for the minimum combination of recent projects that cover the entire county */
  const fullCoverageCombos = []
  const partialCoverageCombos = []
  for (let combo of combos) {
    if (fullCoverageCombos.some(c => isStrictSuperset(combo, c.projects))) {
      if (!silent) {
        console.log('Skipping', combo.map(p => p.project.properties.workunit))
      }
      continue
    }

    const union = combo.length === 1
      ? combo[0].project
      : turf.union(turf.featureCollection(combo.map(p => turf.feature(p.project).geometry)))
    const coverage = analyzeCoverage(county, union)

    if (!silent) {
      console.log(combo.map(p => p.project.properties.workunit), coverage)
    }

    if (coverage >= FULL_COVERAGE_MINIMUM) {
      fullCoverageCombos.push({ projects: combo, coverage: Math.min(coverage, 1) })
    } else {
      partialCoverageCombos.push({ projects: combo, coverage })
    }
  }

  const output = { 
    name: county.properties.NAME, 
    lsad: county.properties.LSAD, 
    state: county.properties.STATE
  }

  if (fullCoverageCombos.length > 0) {
    output.full_coverage = true

    for (let i = 0; i < fullCoverageCombos.length; i++) {
      output[`projects_${i + 1}`] = fullCoverageCombos[i].projects.map(p => p.project.properties.workunit).join('|')
      output[`projects_${i + 1}_coverage`] = fullCoverageCombos[i].coverage
    } 
  } else {
    output.full_coverage = false

    const ordered = orderBy(partialCoverageCombos, [
        s => s.coverage, 
        s => Math.max(...s.projects.map(p => p.project.properties.collect_end))
      ], 
      ['desc', 'desc']
    )

    for (let i = 0; i < Math.min(3, ordered.length); i++) {
      output[`projects_${i + 1}`] = ordered[i].projects.map(p => p.project.properties.workunit).join('|')
      output[`projects_${i + 1}_coverage`] = ordered[i].coverage
    }
  }

  /** Always assume the first project set is correct */
  let useProjects = output['projects_1'].split('|')

  const groups = []
  const insignificantOrphans = []

  while (useProjects.length > 0) {
    const projectKey = useProjects[0]
    const project = countyProjects[projectKey]

    const coverage = analyzeCoverage(county, project)

    if (coverage >= SIGNIFICANT_COVERAGE_MINIMUM) {
      const newGroup = [projectKey]

      for (let i = useProjects.length - 1; i > 0; i--) {
        const currentProjectKey = useProjects[i]
        const currentProject = countyProjects[currentProjectKey]

        const hasSameParent = currentProject.properties.project_id === project.properties.project_id
        const hasSimilarAge = (Math.abs(currentProject.properties.collect_end - project.properties.collect_end) / (1000 * 60 * 60 * 24)) <= MAXIMUM_COMBINABLE_AGE_GAP_DAYS

        const shouldCombine = hasSameParent || hasSimilarAge

        if (shouldCombine) {
          newGroup.push(currentProjectKey)
          useProjects = useProjects.splice(i, 1)
        }
      }

      groups.push(newGroup)
    } else {
      insignificantOrphans.push(projectKey)
    }
  }

  for (let orphan of insignificantOrphans) {
    let mostIntersect = 0
    let bestGroup = null

    for (let i = 0; i < groups.length; i++) {
      const group = groups[i]
      const groupGeometry = turf.union(turf.featureCollection(group.map(p => turf.feature(countyProjects[p]).geometry)))
      const intersect = turf.intersect(turf.featureCollection([turf.feature(countyProjects[orphan]).geometry, groupGeometry]))
      const area = turf.area(intersect)

      if (area > mostIntersect) {
        bestGroup = group
      }
    }

    if (bestGroup === null) {
      let closestTime = Infinity

      for (let i = 0; i < groups.length; i++) {
        const group = groups[i]

        for (let j = 0; j < group.length; j++) {
          const project = countyProjects[group[j]]

          const diff = Math.abs(project.properties.collect_end - countyProjects[orphan].properties.collect_end)
          if (diff < closestTime) {
            closestTime = diff
            bestGroup = i
          }
        }
      }
    }

    groups[bestGroup].push(orphan)
  }

  output.groups = groups
  
  return output
}

if (require.main === module) {
  console.log(main(process.argv[2]))
}

module.exports = main