
from multiprocessing.dummy import Pool as ThreadPool
import subprocess

NUM_THREADS = 96

def process(i):
  print(f'Processing {str(i)}')
  subprocess.run(["node", "Copy_DEMs_To_County_Tif_Files_UTM_Folder.js", str(i)])

def main():
    pool = ThreadPool(NUM_THREADS)
    pool.map(process, range(134))
    pool.close()
    pool.join()

if __name__ == '__main__':
  main()
