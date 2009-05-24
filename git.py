#!/usr/bin/env python

from __future__ import with_statement

from errno import EACCES
from os.path import realpath
from sys import argv, exit

import os

from fuse import FUSE, Operations, LoggingMixIn
from util import format_metadata

class Git(LoggingMixIn, Operations):    
    def __init__(self, local_path, new=False):
        self.local_repo = realpath(local_path) + "/metadata"
        
        if(new):
            # there should probably be error checking here
            os.mkdir(self.local_repo)
            os.chdir(self.local_repo)
            os.system("echo git init")
            os.system("git init")
            format_metadata(self.local_repo + "/metadata.xml")
            os.system("git add metadata.xml")
            os.system("git commit -m 'initial commit'")
            os.system("echo git branch local")
            os.system("git branch local")
            os.system("echo git checkout local")
            os.system("git checkout local")
        
    def __call__(self, op, path, *args):
        return LoggingMixIn.__call__(self, op, self.root + path, *args)

    def clone(self, upstream_repo):
        return os.system("git clone %s %s" % (upstream_repo, self.local_repo))

    def pull(self, upstream_repo, clobber=True):
        # pull metadata from upstream path
        # change dir to the local repo
        os.chdir(self.local_repo)

        if clobber:
            # pull from upstream_repo into master
            os.system("git pull %s master master" % upstream_repo)

            # merge master into local
            if(0 != os.system("git checkout local")):
               os.system("git checkout -b local")
            return os.system("git merge master")

        else:
            raise Exception("Non-clobbering metadata pull not implemented")
            # do a diff of working metadata file
            # examine timestamps in diff, resolve accordingly

    def push(self, upstream_repo):
        os.chdir(self.local_repo)
        return os.system("cd %s && git push %s master" % (self.local_repo, upstream_repo)) 

