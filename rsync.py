#!/usr/bin/env python

from __future__ import with_statement

from errno import EACCES
from os.path import realpath
from sys import argv, exit

import os

from fuse import FUSE, Operations, LoggingMixIn
from metadata import Metadata

class Git(LoggingMixIn, Operations):    
		
	def __init__(remote,remotedir):
		self.remotehost = remote
		self.remotedir = remotedir

	def push(filename)
		command = "rsync -azc " + filename + " " + self.remotehost + ":" + self.remotedir + filename
		os.system(command)
	
