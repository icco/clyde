#!/usr/bin/env python

from collections import defaultdict
from errno import ENOENT, ENOTDIR
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
import os

from fuse import FUSE, Operations, LoggingMixIn
from metadata import Metadata, file_defaults, file_attributes
from loopback import Loopback

from xml.dom.minidom import parse

class Clyde(LoggingMixIn, Operations):
    
    def __init__(self, local_storage_path, mount_point, clone_addr=None):
        self.metadata = Metadata(local_storage_path)
        self.loopback = Loopback(local_storage_path+'/files')
        self.local_storage = local_storage_path+'/files/'
       
    def chmod(self, path, mode):
        return self.metadata.chmod(path, mode)

    def chown(self, path, uid, gid):
        return self.metadata.chown(path, uid, gid)
    
    def create(self, path, mode):
        self.metadata.create(path, mode)
        return self.loopback("create", path,  mode)
       
    def getattr(self, path, fh=None):
        '''
         Policy G1: if m_time of a local version of file == m_time of home verision then
                    file is either the home or a cached version that is ok to use
        '''
        if metadata.isHome(path):
           st = loopback("getattr", path)
        else:
           st = metadata("getattr", path)

        return st


    def mkdir(self, path, mode):
        return self.metadata.mkdir(path, mode)
    
    def open(self, path, flags):
        '''
         Policy O1: only read home or cached files
                    cached files must be 'recent'
         *Policy O2: if file is too large for current device, do not open and report to user
         Policy O3: if home computer is offline look for an alternative version
                    must flag metadata so home knows to update when online
        '''
        if metadata.isHome(path):
           return self.loopback("open", path, flags)
        else:
           print("This is where I should rsynch")
           raise OSError(ENOENT)
    
    def read(self, path, size, offset, fh):
        return self.loopback("read", path, size, offset, fh)
    
    def readdir(self, path, fh):
        return self.metadata.readdir(path, fh)
    
    def readlink(self, path):
        return self.data[path]
    
    def rename(self, old, new):
        return self.loopback("rename", old, new)
    
    def rmdir(self, path):
        return self.metadata.rmdir(path)
    
    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)
    
    def symlink(self, target, source):
        return self.loopback("symlink", source, target)
    
    def truncate(self, path, length, fh=None):
        self.loopback("truncate", path, length, None)
        return 0
    
    def unlink(self, path):
        return 0
    
    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.loopback("utimens", path, (atime, mtime))
        return self.metadata("utimens", path, (atime, mtime))
    
    def write(self, path, data, offset, fh):
        '''
         Policy W1: update metadata file with stat info on every write 
        '''
        return self.loopback("write", path, data, offset, fh)

    def release(self, path, fh):
        return self.loopback("release", path, fh)

    def flush(self, path, fh):
        return self.loopback("flush", path, fh)

    def fsync(self, path, datasync, fh):
        return self.loopback("fsync", path, datasync, fh)

    def read_files_from_xml(self, path):
        dom = parse("metadata.xml")
        entries = dom.getElementsByTagName("file")
        for file in entries:
            path = file.getAttribute("path")
            self.id_counter += 1
            self.files[path] = dict()

            print "file: %s" % path

            for key in file_attributes:
               if file.hasAttribute(key):
                  self.files[path][key] = int(file.getAttribute(key))
                  print "key: %s,  value: %s" % (key, file.getAttribute(key))
               else:
                  self.files[path][key] = file_defaults[key]
                  print "key: %s,  default: %s" % (key, file_defaults[key])

if __name__ == "__main__":
    if len(argv) < 3 :
        print 'usage: %s <local storage> <mountpoint>' % argv[0]
        exit(1)

    clone_addr = None 

    if (len(argv) >= 4):
        clone_addr = argv[3]
      
    fuse = FUSE(Clyde(argv[1], argv[2], clone_addr), argv[2], foreground=True)
