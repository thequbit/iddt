#!/bin/bash

python worker.py start /tmp/worker-0.pid; sleep 1;
python worker.py start /tmp/worker-1.pid; sleep 1;
python worker.py start /tmp/worker-2.pid; sleep 1;
python worker.py start /tmp/worker-3.pid; sleep 1;

python worker.py start /tmp/worker-4.pid; sleep 1;
python worker.py start /tmp/worker-5.pid; sleep 1;
python worker.py start /tmp/worker-6.pid; sleep 1;
python worker.py start /tmp/worker-7.pid; sleep 1;

python worker.py start /tmp/worker-8.pid; sleep 1;
python worker.py start /tmp/worker-9.pid; sleep 1;
python worker.py start /tmp/worker-10.pid; sleep 1;
python worker.py start /tmp/worker-11.pid; sleep 1;

python worker.py start /tmp/worker-12.pid; sleep 1;
python worker.py start /tmp/worker-13.pid; sleep 1;
python worker.py start /tmp/worker-14.pid; sleep 1;
python worker.py start /tmp/worker-15.pid; sleep 1;


