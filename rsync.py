#!/usr/bin/env python

# Byahh.

from errno import EACCES
from os.path import realpath
from sys import argv, exit

import os

from metadata import Metadata

class Rsync():    
	def __init__(self, remote, remotedir):
		self.remotehost = remote
		self.remotedir = remotedir

	def push(self, filename):
		# a : Archival
		# z : compression
		# --safe-links : don't get symlinks
		command = "rsync -az --safe-links " + filename + " " + self.remotehost + ":" + self.remotedir + "/" + filename
		print command
		os.system(command)
	
	def pull(self, filename):
		command = "rsync -az --safe-links " + self.remotehost + ":" + self.remotedir + "/" + filename  + " " + filename 
		print command
		os.system(command)

