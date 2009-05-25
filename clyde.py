#!/usr/bin/env python

from collections import defaultdict
from errno import ENOENT, ENOTDIR
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time

# Our stuff plus
from fuse import FUSE, Operations, LoggingMixIn
from metadata import Metadata, file_defaults, file_attributes
from loopback import Loopback
from rsync import Rsync

from xml.dom.minidom import parse

class Clyde(LoggingMixIn, Operations):
    
    def __init__(self, local_storage_path, mount_point, clone_addr=None):
        self.metadata = Metadata(local_storage_path)
        self.loopback = Loopback(local_storage_path + "/files")
       
    def chmod(self, path, mode):
        return self.metadata.chmod(path, mode)

    def chown(self, path, uid, gid):
        return self.metadata.chown(path, uid, gid)
    
    def create(self, path, mode):
        return self.metadata.create(path, mode)
       
    def getattr(self, path, fh=None):
        return self.metadata.getattr(path, fh)
        
    def mkdir(self, path, mode):
        return self.metadata.mkdir(path, mode)
    
    def open(self, path, flags):
        return self.loopback.open(path, flags)
    
    def read(self, path, size, offset, fh):
        return self.loopback.read(path, size, offset, fh)
    
    def readdir(self, path, fh):
        return self.metadata.readdir(path, fh)
    
    def readlink(self, path):
        return self.data[path]
    
    def rename(self, old, new):
        self.files[new] = self.files.pop(old)
        return 0
    
    def rmdir(self, path):
        self.files.pop(path)
        return 0
    
    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)
    
    def symlink(self, target, source):
        self.files[target] = dict(st_mode=(S_IFLNK | 0777), st_nlink=1,
            st_size=len(source))
        self.data[target] = source
        return 0
    
    def truncate(self, path, length, fh=None):
        self.data[path] = self.data[path][:length]
        self.files[path]['st_size'] = length
        return 0
    
    def unlink(self, path):
        self.files.pop(path)
        return 0
    
    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime
        return 0
    
    def write(self, path, data, offset, fh):
        self.data[path] = self.data[path][:offset] + data
        self.files[path]['st_size'] = len(self.data[path])
        return len(data)
	
	def flush(self, path, fi):
		return 0


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
