# userThreadTest.py
# CS3070 Synchronization Lab series
#
# created: Spring '16
# updated: 10 Dec 2024

from multiprocessing import Queue  #https://docs.python.org/3.11/library/multiprocessing.html
#imports queue module for instantiation
import os
#imports os module
import time
#imports time module

from support import SL_Thread


def f(q, word):
    ''' An example function to call.
        -q is a multiprocessing.Queue object
        -word is a string '''
    q.put(word)
    #puts the word into the queue
    print("in f(), pid =" + str( os.getpid() ) + '\n')

####################################
####################################
####################################
#script starts here
##

if __name__ == '__main__':
    q = Queue()
    
    t1 = SL_Thread.SL_Thread(f, (q,42))
    t2 = SL_Thread.SL_Thread(f, (q,'testing'))
    t3 = SL_Thread.SL_Thread(f, (q,'hello'))

    start = time.time()
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    finish = time.time()
    print("joined")

    while not q.empty():
        print(q.get(), ' ', end = '')
        #takes the item from the queue
    print()
    
    print('processing took', (finish - start), 'sec')