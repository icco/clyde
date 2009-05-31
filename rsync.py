#!/usr/bin/env python

# Byahh.

from errno import EACCES
from os.path import realpath
from sys import argv, exit

import os

class Rsync():    
	def __init__(self, remote, remotedir):
		self.remotehost = remote
		self.remotedir = remotedir
		# a : Archival
		# z : compression
		# --safe-links : don't get symlinks
		self.attributes = "-az --safe-links "

	def push(self, filename):
		command = "rsync " + self.attributes + " " + filename + " " + self.remotehost + ":" + self.remotedir + "/" + filename
		os.system(command)
	
	def pull(self, filename):
		command = "rsync " + self.attributes + " " + self.remotehost + ":" + self.remotedir + "/" + filename  + " " + filename 
		os.system(command)

