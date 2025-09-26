const fs = require('fs')
const { Readable } = require('stream');
const { fromArrayBuffer } = require('geotiff')
const { S3Client, GetObjectCommand  } = require("@aws-sdk/client-s3")

const s3Config = {
  region: 'us-west-2'
}

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

const validateTif = async (path) => {
  try {
    //Validate file is not corrupt
    const buffer = fs.readFileSync(path)
    const arrayBuffer = buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
    const tiff = await fromArrayBuffer(arrayBuffer)

    //If file is corrupt next step will throw exception
    const image = await tiff.getImage()
  } catch (error) {
    return false
  }

  return true
}

const getFile = async (url) => {
  const client = new S3Client(s3Config);
  const input = { // GetObjectRequest
    Bucket: "prd-tnm", // required
    Key: url.replace('https://prd-tnm.s3.amazonaws.com/', ''), // required
    ChecksumMode: "ENABLED",
  };
  const command = new GetObjectCommand(input);
  const response = await client.send(command);

  return response.Body
}

const main = async (url, path, i = 1, count = 1) => {
  let success = false
  while (!success) {
    try {
      let valid = false

      if (fs.existsSync(path)) {
        valid = await validateTif(path)

        if (valid) {
          console.log(`(${i}/${count}) ALREADY DOWNLOADED ${url} => ${path}. SKIPPING.`)
        } else {
          console.log(`(${i}/${count}) PREVIOUSLY DOWNLOADED TIF FILE IS INVALID ${url} => ${path}`, valid)
          console.log('CHECKPOINT')
        }
      }

      while (!valid) {
        console.log(`(${i}/${count}) DOWNLOADING ${url} => ${path}`)
        try {
          const response = await getFile(url)
          const stream = response.pipe(fs.createWriteStream(path))

          await new Promise(resolve => stream.on('finish', resolve))

          valid = await validateTif(path)

          if (valid) {
            console.log(`(${i}/${count}) SUCCESSFULLY DOWNLOADED ${url} => ${path}`)
          } else {
            console.log(`(${i}/${count}) TIF FILE IS INVALID ${url} => ${path}`)
          }
        } catch (error) {
          console.log(error)
          // console.log(`(${i}/${count}) FAILED TO FETCH ${url} => ${path}. RETRYING.`)

          //Sleep in order to clear console log buffer
          await new Promise((resolve, reject) => {
            setTimeout(resolve, 0)
          })
        }
      }

      success = true
    } catch (error) {
      console.log('ERROR', error)
    }
  }

  return true
}

if (require.main === module) {
  main(...process.argv.slice(2))
}

module.exports = main
