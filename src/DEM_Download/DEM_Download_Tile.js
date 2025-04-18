const fs = require('fs')

const main = async (url, path, i = 1, count = 1) => {
  while (!fs.existsSync(path)) {
    console.log(`(${i}/${count}) Downloading ${url}`)
    try {
      const res = await fetch(url);
      const fileStream = fs.createWriteStream(path);
      await new Promise((resolve, reject) => {
        res.body.pipe(fileStream);
        res.body.on("error", reject);
        fileStream.on("finish", resolve);
      });
    } catch (error) {
      console.log(`FAILED TO FETCH ${path}. RETRYING. ERROR: `, error)
    }
  }
}

if (require.main === module) {
  main(process.argv.slice(2))
}

module.exports = main