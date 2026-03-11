#
# ATMServer.py
# CS3070 Synchronization Lab series
#
# created: Spring '16
# updated: 13 Jan 2022 (+ M5 fixes: semaphore + delta application)
#

import random
import time
import multiprocessing as mp

import SL_Kernel as Kernel
from Semaphore import *
from ATMMessage import *

'''This is bank's ATM server class.
There are multiples of these running at the bank which may access the same accounts at the same time. It
does not matter if we think of them running on the same huge machine or many little ones, the data is shared.

It does not matter if the data is shared inside a database, a data structure, in a Non Uniform Memory Access
RAM, or in a sandard RAM.  Shared is shared and essentially the only thing that changes is timing.
'''
class ATMServer(mp.Process):

##########################################
#Constructor

    def __init__(self, cName, pName, seed, account, transactionLimit, n, simArgs, atm_connection, kernel_connection):
        super().__init__(target=self.execute, args=simArgs )

        #hardware initialization
        self.OS = Kernel.SL_Kernel(kernel_connection, n, account)
        self.clientName = cName
        self.name = pName
        self.account = account
        self.flag = mp.Event()
        self.flag.clear()

        self.atm_connection = atm_connection
        self.__TRANSACTION_LIMIT__ = transactionLimit
        self.again = True
        self.seed = seed

##########################################
#Instance Methods

    def execute(self, q, al, ml, n):
        '''this is the function which serves as the processes "Run loop" '''

        self.__initializeSimComponents(q, al)
        self.semaphore = Semaphore(n, self.OS)

        # This server talks to exactly one ATM over self.atm_connection.
        # Track the last balance we returned to THIS client so we can derive deltas on PUT.
        last_read = None

        i = 0
        while self.again:

            #check and act on sim's stop condition
            if i >= self.__TRANSACTION_LIMIT__:
                self.again = False
                break

            i += 1

            #waiting for next message
            message = self.atm_connection.recv()
            (operation, amount) = ATMMessage.unwrap(message)

            if operation == PUT_BALANCE:
                # Client sends an absolute new balance it computed from its last read.
                if last_read is None:
                    # In this lab, ATM always does GET before any PUT, but guard just in case.
                    # Treat this as a delta from current state if GET never happened.
                    self.semaphore.wait(self)
                    try:
                        cur = self.getBalance()
                        new_balance = amount  # absolute write fallback (shouldn't happen in normal flow)
                        # Prefer delta behavior even here to avoid clobber: apply (amount - cur)
                        delta = amount - cur
                        new_balance = cur + delta
                        self.putBalance(new_balance)
                        last_read = new_balance
                    finally:
                        self.semaphore.signal(self)
                else:
                    # Normal path: derive the intended change and apply it atomically to CURRENT state
                    delta = amount - last_read

                    self.semaphore.wait(self)
                    try:
                        cur = self.getBalance()
                        new_balance = cur + delta
                        self.putBalance(new_balance)
                        # Keep our notion in sync with what the client would see next
                        last_read = new_balance
                    finally:
                        self.semaphore.signal(self)

            elif operation == GET_BALANCE:
                # Read the current shared state under the semaphore
                self.semaphore.wait(self)
                try:
                    cur = self.getBalance()
                    last_read = cur
                finally:
                    self.semaphore.signal(self)

                # Send the reply outside the critical section
                msg = ATMMessage.wrap(BALANCE, cur)
                self.atm_connection.send(msg)

            else:
                raise RuntimeError(operation + 'is an unrecognized account operation')

        self.atm_connection.send(SHUTDOWN)   #tell ATM to shutdown
        print('   ATMServer', self.clientName, 'shut down')
        self.OS.completeShutDown()

    def getBalance(self):
        return self.OS.read(self.account)

    def putBalance(self, newBalance):
        self.OS.write(self.account, newBalance)

    def __initializeSimComponents(self, q, al):
        self.OS.SIM_SETUP_setUpKernel(q, al, self.name)
        #random.seed(self.seed)
        self.OS.p = self

        self.OS.al = self.OS.Lock(self.OS)
        self.OS.read(self.account)                    #verify we are connected to proper memory

    def getName(self):
        ''' returns the string that is the name of thie UserProcess'''
        return self.name

    def start(self):
        ''' This is how we get Python to run our custom code in a process.
            when start() is called on a process in our code, we just pass
            along that call to the actual Process object.
            The process object will execute the function we provide to its target
            parameter
            If we want a process to last a long time we put a long duration loop
            the function provided to target.
        '''
        super().start()

    def join(self):
        ''' Send a message to parent calling this when complete, parent will wait until all joining
            children have completed before progressing past join barrier. '''
        super().join()

    def sleep(self):
        '''puts thread into wait state'''
        #print('      calling for sleep (via wait) on', self.name)
        self.flag.wait()

    def wake(self):
        '''puts thread back into running state '''
        self.flag.set()   #wake the process' thread up

    def slp_yield(self):
        '''tells scheduler to take thread off CPU and put into ready queue'''
        self.flag.wait(0.0001)