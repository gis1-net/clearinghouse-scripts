const fs = require('fs')
const { Readable } = require('stream');

const responseToReadable = response => {
  const reader = response.body.getReader();
  const rs = new Readable();
  rs._read = async () => {
      const result = await reader.read();
      if (!result.done){
          rs.push(Buffer.from(result.value));
      } else{
          rs.push(null);
          return;
      }
  };
  return rs;
};

const main = async (url, path, i = 1, count = 1) => {
  if (fs.existsSync(path)) {
    console.log(`(${i}/${count}) ALREADY DOWNLOADED ${path}. SKIPPING.`)
  }
  while (!fs.existsSync(path)) {
    console.log(`(${i}/${count}) DOWNLOADING ${url} => ${path}`)
    try {
      const response = await fetch(url)
      responseToReadable(response).pipe(fs.createWriteStream(path))
      console.log(`SUCCESSFULLY DOWNLOADED ${path}`)
    } catch (error) {
      console.log(`FAILED TO FETCH ${url}. RETRYING.`)
    }
  }
}

if (require.main === module) {
  main(...process.argv.slice(2))
}

module.exports = main