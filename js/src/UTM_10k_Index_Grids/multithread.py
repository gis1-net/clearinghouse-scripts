
from multiprocessing.dummy import Pool as ThreadPool
import subprocess

NUM_THREADS = 8

def process(i):
  print(f'Processing {str(i)}')
  subprocess.run(["node", "Generate_UTM_10k_Index_Grids_By_State.js", str(i)])

def main():
    pool = ThreadPool(NUM_THREADS)
    pool.map(process, range(51))
    pool.close()
    pool.join()

if __name__ == '__main__':
  main()
