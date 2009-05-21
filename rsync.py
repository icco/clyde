#!/usr/bin/env python

from __future__ import with_statement

from errno import EACCES
from os.path import realpath
from sys import argv, exit

import os

from fuse import FUSE, Operations, LoggingMixIn
from metadata import Metadata

class Git(LoggingMixIn, Operations):    

	def __init__():
		localhost = socket.gethostbyaddr(socket.gethostname())

	def push(filename)
		os.system("rsync -azc %s %s:%s%s",filename,remotehost,remotedir,filename)
	
