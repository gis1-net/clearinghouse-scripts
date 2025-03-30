
from multiprocessing.dummy import Pool as ThreadPool
import subprocess

def process(i):
  print(f'Processing {str(i)}')
  subprocess.run(["node", "intersect.js", str(i)])

def main():
    pool = ThreadPool(16)
    pool.map(process, range(3143))
    pool.close()
    pool.join()

if __name__ == '__main__':
  main()
