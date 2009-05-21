#!/usr/bin/env python

from __future__ import with_statement

from errno import EACCES
from os.path import realpath
from sys import argv, exit
from xml.dom.minidom import parse
from xml.dom.minidom import Document

import os

from fuse import FUSE, Operations, LoggingMixIn
from metadata import Metadata

class Rsync():    
	def __init__(self, remotehost):	
		self.__init__(self, remotehost,"/fuse")

	def __init__(self, remote, remotedir):
		self.remotehost = remote
		self.remotedir = remotedir

	def push(self, filename):
		# a : Archival
		# z : compression
		# --safe-links : don't get symlinks
		command = "rsync -az --safe-links " + filename + " " + self.remotehost + ":" + self.remotedir + filename
		os.system(command)
	
