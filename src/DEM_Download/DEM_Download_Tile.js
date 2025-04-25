const fs = require('fs')

const responseToReadable = response => {
  const reader = response.body.getReader();
  const rs = new Readable();
  rs._read = async () => {
      const result = await reader.read();
      if(!result.done){
          rs.push(Buffer.from(result.value));
      }else{
          rs.push(null);
          return;
      }
  };
  return rs;
};

const main = async (url, path, i = 1, count = 1) => {
  while (!fs.existsSync(path)) {
    console.log(`(${i}/${count}) Downloading ${url}`)
    try {
      const response = fetch(url)
      responseToReadable(response).pipe(fs.createWriteStream(path))
    } catch (error) {
      console.log(`FAILED TO FETCH ${path}. RETRYING. ERROR: `, error)
    }
  }
}

if (require.main === module) {
  main(...process.argv.slice(2))
}

module.exports = main