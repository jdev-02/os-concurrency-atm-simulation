'''
Semaphore.py
CS3070: , ,  

Created: Spring '16
Updated: 13 Jan 2022
'''

'''This is the Semaphore implementation class.'''

class Semaphore(object):
##########################################
#Constructor

    def __init__(self, counter, simKernel):
        ''' use as provided.
            - n is the number to set the Semaphore counter to initially
            - simKernel provides the access to the simulated kernel a real OS
                 would have when constructing a Semaphore
            This constructor will run once when the OS invokes it.
        '''
        
        self.OS = simKernel
        self.counter = 1 #Assign counter initial value of 1 (lock is open)
        self.queue = [] #create abstract queue
        self.lock = self.OS.getAtomicLock() #create lock
        
##########################################
#Instance Methods

    def wait(self, caller):
        ''' semaphore wait functionality.
            - caller is the process asking "wait?"
              (you will need caller because this is a simulated system,
               a production OS has this info available as part of the PCB)
        '''
        if (self.counter == 1):
            #lock is open
            self.lock.acquire(caller)
            #caller gets atom lock
            self.counter = 0
        elif (self.counter == 0):
            #place waiting process in queue bc resource is locked, go to sleep
            self.queue.append(caller)
            caller.sleep()
            
    def signal(self, caller):
        ''' semaphore signal functionality.
            - caller is the process providing the "signal"
              (you will need caller because this is a simulated system,
               a production OS has this info available as part of the PCB)
        '''
        #release lock from current process
        self.lock.release(caller)
        if len(self.queue) > 0:
            #get next man up
            nextMan = self.queue.pop(0)
            self.OS.wake(nextMan)
        else:
            self.counter = 1 
            #resource is free to be grabbed by an incoming process since nothing is in the queue waiting

#EOF