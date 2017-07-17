#!/usr/bin/env python

from multiprocessing import Process
from logIoc import logIoc
from threading import Thread
import multiprocessing
import subprocess

lio=logIoc()
lio.query_proc_start()
#xlio=logIoc()
#processes=[]
#p=Process(target = lio.query_proc_start(),)
#p.start()
#processes.append(p)
#p1=Process(target = xlio.batch_cycler(),)
