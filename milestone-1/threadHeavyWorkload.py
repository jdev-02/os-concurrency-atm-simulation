#
# userThreadPerformanceTest.py
# CS3070 Synchronization Lab series
#
# created: Spring '16
# updated: 10 Dec 2024
#

from multiprocessing import Queue  #https://docs.python.org/3.11/library/multiprocessing.html
import os
import time
import sys

from support import SL_Thread
from support import p7


def f(q, candidate):
    answer = p7.isPrime(candidate)
    q.put((candidate, answer))
    print("in f(), pid =" + str( os.getpid() ) + '\n')

if __name__ == '__main__':
    q = Queue()
    
    t1 = SL_Thread.SL_Thread(f, (q,149996387363))
    t2 = SL_Thread.SL_Thread(f, (q,149996387377))
    t3 = SL_Thread.SL_Thread(f, (q,149996387369))

    print("running, calling for thread starts, this may take up to 20 sec")
    start = time.time()
    t1.start()
    t2.start()
    t3.start()

    t3.join()
    t2.join()
    t1.join()
    finish = time.time()
    print("joined")
 
    while not q.empty():
        print(str(q.get()), ' ', end = '') 
    print()

    print('processing took', (finish - start), 'sec')



