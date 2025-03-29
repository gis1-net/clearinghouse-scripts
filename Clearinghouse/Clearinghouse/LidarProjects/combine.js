const fs = require('fs')
const projects = {
  a: require('./county_projects_A.json'),
  b: require('./county_projects_B.json'),
  c: require('./county_projects_C.json'),
  d: require('./county_projects_D.json'),
  e: require('./county_projects_E.json'),
  f: require('./county_projects_F.json'),
  g: require('./county_projects_G.json'),
  h: require('./county_projects_H.json'),
  i: require('./county_projects_I.json'),
  j: require('./county_projects_J.json'),
  k: require('./county_projects_K.json'),
  l: require('./county_projects_L.json'),
  m: require('./county_projects_M.json'),
  n: require('./county_projects_N.json'),
  o: require('./county_projects_O.json'),
  p: require('./county_projects_P.json'),
  q: require('./county_projects_Q.json'),
  r: require('./county_projects_R.json'),
  s: require('./county_projects_S.json'),
  t: require('./county_projects_T.json'),
  u: require('./county_projects_U.json'),
  v: require('./county_projects_V.json'),
  w: require('./county_projects_W.json'),
  x: require('./county_projects_X.json'),
  y: require('./county_projects_Y.json'),
  z: require('./county_projects_Z.json')
}

const main = async () => {
  const keys = Object.keys(projects)
  const output = []

  for (const key of keys) {
    output.push(...projects[key])
  }

  fs.writeFileSync('./County_Projects.json', JSON.stringify(output, null, 2))
}

main()