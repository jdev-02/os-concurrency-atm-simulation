# OS Concurrency — ATM Simulation

A multi-milestone operating systems lab simulating concurrent ATM transactions using semaphores for synchronization.

## Problem

Multiple ATM processes access shared bank accounts simultaneously. Without synchronization, concurrent reads and writes produce **lost updates** — a classic race condition where one ATM's transaction overwrites another's.

## Solution Approach

The simulation evolved across 5 milestones:

| Milestone | Focus |
|-----------|-------|
| `milestone-1` | Threading fundamentals — trivial vs heavy workload thread comparison |
| `milestone-2` | Initial ATM client/server with semaphore-based mutual exclusion |
| `milestone-3` | Correctness analysis and protocol refinement |
| `milestone-4` | Semaphore implementation improvements |
| `milestone-5` | **Final** — delta-based update protocol |

## Key Technical Decision: Delta Updates

The final version solves the lost-update problem by having ATM clients send **deltas** (the change in balance) rather than absolute values. When ATM-A and ATM-B both read balance $1000 and each try to withdraw $100, sending absolute value $900 causes one update to be lost. Sending delta -$100 allows the server to correctly apply both: $1000 - $100 - $100 = $800.

## Architecture

```
ATMServer.py    — bank server; holds account balances; enforces mutual exclusion via Semaphore
ATM.py          — ATM client process; sends transactions to server
ATMMessage.py   — message format for client-server communication
Semaphore.py    — synchronization primitive (wait/signal protocol)
atmProblem.py   — simulation driver; spawns ATM clients
```

## Technologies

Python · Multiprocessing · Semaphores · IPC

## Background

Naval Postgraduate School · CS3070 Operating Systems · 2025
3-person team project (Gohlwar, Goohs, Norman). Milestone-5 final implementation developed collaboratively.
