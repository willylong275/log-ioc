#!/usr/bin/env python
from logIoc import logIoc
x=logIoc()
newlist = []
newlist = x.get_hits()
for line in newlist:
	print line
