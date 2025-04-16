const { orderBy } = require('lodash')

const tap = (value, callback) => {
  callback(value)
  return value
}

const buildCombosRecursive = (set) => {
  if (set.length === 0) {
    return [set]
  }

  const subCombos = buildCombosRecursive([...set].slice(1))

  const result = []

  for (let subCombo of subCombos) {
    result.push(subCombo)
  }
  
  for (let subCombo of subCombos.map(sc => tap([...sc], v => v.unshift(set[0])))) {
    result.push(subCombo)
  }

  return orderBy(result, e => e.length, 'desc')
}

const buildCombos = (set) => {
  return buildCombosRecursive(set)
    .filter(e => e.length)
    .reverse()
}

const isStrictSuperset = (setA, setB) => {
  const isSuperset = setB.every(val => setA.includes(val))

  if (isSuperset) {
    const lastPosition = setB.length - 1
    const lastElement = setB[lastPosition]

    if (setA[lastPosition] === lastElement) {
      return true
    }
  }

  return false
}

const dedupeSupersets = (sets) => {
  const deduped = []
  for (let i = sets.length - 1; i >= 0; i--) {
    let isDupe = false;

    for (let j = 0; j < i; j++) {
      if (isStrictSuperset(sets[i], sets[j])) {
        isDupe = true
        break
      }
    }

    if (!isDupe) {
      deduped.push(sets[i])
    }
  }

  return deduped.reverse()
}

module.exports = { buildCombos, isStrictSuperset, dedupeSupersets }