import json
import urllib.request
import os
from multiprocessing.dummy import Pool as ThreadPool

DESTINATION_FOLDER = ''
URLS = []

def downloadTile(args):
  global DESTINATION_FOLDER
  global URLS

  (i, url) = args

  parts = url.split('/')

  folder = os.path.join(DESTINATION_FOLDER, parts[-3])
  if not os.path.isdir(folder):
    os.mkdir(folder)
    print(f"Created {parts[-3]} folder")

  print(f"({i}/{len(URLS)}) Downloading {url}...")

  retry = 3

  while retry > 0:
    try: 
      urllib.request.urlretrieve(url, os.path.join(folder, parts[-1]))
    except:
      retry -= 1
      print(f"Download for {url} failed, retrying ({retry} more attempts)...")

def main():
  global DESTINATION_FOLDER
  global URLS

  state = input("Enter the name of the state (e.g. South Carolina): ")
  DESTINATION_FOLDER = input("Enter the name of the folder to which DEM files should be downloaded (e.g. W:\\SOUTH_CAROLINA): ")
  threadCount = int(input("How many threads do you want to use (default: 32): ").strip() or "32")

  projects = []
  usgs1mProjects = []

  with open('County_Projects.json') as file:
    projects = json.load(file)

  with open('USGS_1m_Projects.json') as file:
    usgs1mProjects = json.load(file)

  stateProjects = set([])

  for p in projects:
    if p['state'].lower() == state.lower() and p['ql'] in ['QL 2', 'QL 1', 'QL 0'] and p['workunit'] in usgs1mProjects:
      stateProjects.add(p['workunit'])

  print(f"Found {len(stateProjects)} projects to download")

  URLS = set([])

  for i, p in enumerate(stateProjects):
    print(f"({i + 1}/{len(stateProjects)}) Fetching download list for {p}...")

    retry = 3

    while retry > 0:
      try: 
        downloadLinksFileUrl = f"https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/1m/Projects/{p}/0_file_download_links.txt"
        file = urllib.request.urlopen(downloadLinksFileUrl)
        contents = file.readlines()

        print(f"Found {len(contents)} tiles to download")

        for j, line in enumerate(contents):
          url = line.strip().decode("utf-8")
          URLS.add(url)

        retry = 0

      except:
        retry -= 1
        print(f"Download failed, retrying ({retry} more attempts)...")

  print(f"Downloading {len(URLS)} tiles...")

  pool = ThreadPool(threadCount)
  pool.map(downloadTile, enumerate(URLS))
  pool.close()
  pool.join()

if __name__ == '__main__':
  main()