'''
Semaphore.py
CS3070: Gohlwar, Goohs, Norman 

Created: Spring '16
Updated: 13 Jan 2022
'''

'''This is the Semaphore implementation class.'''

class Semaphore(object):
##########################################
#Constructor

    def __init__(self, n, simKernel):
        ''' use as provided.
            - n is the number to set the Semaphore counter to initially
            - simKernel provides the access to the simulated kernel a real OS
                 would have when constructing a Semaphore
            This constructor will run once when the OS invokes it.
        '''
        
        self.OS = simKernel
        # Create counter (located in shared memory) with init value n
        self.OS.write("accountName", n)     
        # Create queue to store processes 
        self.queue = self.OS.getQueue() 
        # Create lock
        self.lock = self.OS.getAtomicLock() 
        
##########################################
#Instance Methods

    def wait(self, caller):
        ''' semaphore wait functionality.
            - caller is the process asking "wait?"
              (you will need caller because this is a simulated system,
               a production OS has this info available as part of the PCB)                 
               
        '''

        # Acquire lock
        self.lock.acquire(caller)
        
        # Assign current counter value to local copy
        counter_state = self.OS.read("accountName")
        # Decrement counter
        counter_state -= 1
        # Write to shared memory
        self.OS.write("accountName", counter_state)
        
        if (counter_state < 0):
            # Critical section in use, need to enter queue
            self.queue.put(caller.getName())
            self.lock.release(caller)
            caller.sleep()
        else:
            # Critical section open
            self.lock.release(caller)
            
    def signal(self, caller):
        ''' semaphore signal functionality.
            - caller is the process providing the "signal"
              (you will need caller because this is a simulated system,
               a production OS has this info available as part of the PCB)
        '''

        # Acquire lock
        self.lock.acquire(caller)

        # Assign current counter value to local copy
        counter_state = self.OS.read("accountName")
        # Increment counter
        counter_state += 1
        # Write to shared memory
        self.OS.write("accountName", counter_state)

        if counter_state <= 0:
            # Get next man from queue, do not modify counter variable since it remains 0
            nextMan = self.queue.get()
            self.OS.wake(nextMan)

            # Prevent race condition of two processes in deadlock
            caller.slp_yield() 

        # Release lock
        self.lock.release(caller)
#EOF