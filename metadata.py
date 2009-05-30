#!/usr/bin/python

from errno import ENOENT, ENOTDIR, ENOTEMPTY
from stat import S_IFREG, S_IFDIR
from xml.dom.minidom import parse
from xml.dom.minidom import Document, Node

from git import Git

from os import access, F_OK, system
from sys import argv, exit
from fuse import FUSE, Operations, LoggingMixIn

from time import time

file_defaults = {}

file_defaults = dict( st_mode=(S_IFREG | 0755), st_atime=23, st_ctime=3, st_mtime=3 )
file_attributes = ('st_atime', 'st_mtime', 'st_ctime', 'st_mode')



class Metadata(Operations, LoggingMixIn):
   def __init__(self, local_storage_path):

      self.fd = 0
      self.xmlpath = local_storage_path + "/metadata/metadata.xml"

      if not(access(local_storage_path + "/metadata", F_OK)):
         self.git = Git(local_storage_path, True)
      else:
         self.git = Git(local_storage_path, False)

      self.files = dict()
      self.files['/'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=0,
         st_mtime=0, st_atime=0)
   
   def __call__(self, op, path, *args):
        return LoggingMixIn.__call__(self, op, path, *args)

   
   def push(self, upstream):
      self.git.push(upstream)

   def pull(self, upstream):
      self.git.pull(upstream)

   def getattr(self, path, fh=None):
      """ 
         return a dict containing file information of remote metadata
         raise an exception if the item is not found
      """
      dom = parse(self.xmlpath)
      node = get_file_node(dom, path)
      file = dict()
      for key in file_attributes:
         if node.hasAttribute(key):
            file[key] = int(node.getAttribute(key))
         else:
            file[key] = file_defaults[key]
      return file

   def readdir(self, path, fh=None):
      dom = parse(self.xmlpath)
      files = ['.', '..'] 
      dir = get_file_node(dom, path)
      for child in dir.childNodes :
         if child.nodeType == child.ELEMENT_NODE:
            files.append(child.getAttribute("d_name"))
       
      return files

   def create(self, path, mode):    
      # prepare File element to be put in metadata
      dom = parse(self.xmlpath)
      root = dom.documentElement

      dir, fname = split_path(path)

      dir_node = get_file_node(dom, dir)
      direntry_node = dom.createElement("Direntry")
      direntry_node.setAttribute("d_name", fname)
      dir_node.appendChild(direntry_node)

      now = str(int(time()))

      new_element = dom.createElement("File")
      new_element.setAttribute("path", path)
      new_element.setAttribute("st_ctime", now)
      new_element.setAttribute("st_atime", now)
      new_element.setAttribute("st_mtime", now)
      new_element.setAttribute("st_mode", str(mode))

      root.appendChild(new_element)

      self.writexml(dom)

      self.fd += 1
      return self.fd

   def mkdir(self, path, mode):
      self.create(path, mode | S_IFDIR)
      return 0

   def rmdir(self, path):
      dom = parse(self.xmlpath)
      if not isDir(dom, path):
         raise OSError(ENOTDIR)
      if path == "/" or not isDirEmpty(dom, path):
         raise OSError(ENOTEMPTY)

      return self.unlink(path)

   def unlink(self, path):
      dir, fname = split_path(path)
      dom = parse(self.xmlpath)
      node = get_file_node(dom, path)
      dirnode = get_file_node(dom, dir)

      node.parentNode.removeChild(node)

      for direntry in dirnode.childNodes:
         if direntry.nodeType == direntry.ELEMENT_NODE and \
          direntry.getAttribute("d_name") == fname:
            dirnode.removeChild(direntry)

      self.writexml(dom)
      
      return 0

   def utimens(self, path, times=None):
      now = time()
      atime, mtime = times if times else (now, now)
      dom = parse(self.xmlpath)
      node = get_file_node(dom, path)
      node.setAttribute("st_atime", str(int(atime)))
      node.setAttribute("st_mtime", str(int(mtime)))

      self.writexml(dom)


   def isHome(self, path):
      node = get_file_node(path)
      return node.getAttribute("home") == this.node

   def writexml(self, dom):
      fp = open(self.xmlpath, "w")
      dom.writexml(fp, newl='\n')
      fp.close()

def isDir(dom, path, node=None):
   if not node:
      node = get_file_node(dom, path)
   return int(node.getAttribute("st_mode")) & S_IFDIR == S_IFDIR

def isDirEmpty(dom, path, node=None):
   if not node:
      node = get_file_node(dom, path)
   return not node.getElementsByTagName("Direntry")


def split_path(path):
   levels = path.split("/")
   fname = levels[-1]
   dir = "/".join(levels[0:-1])

   if(dir == ""):
      dir = "/"

   return (dir, fname)


def get_dir_names(dom, path):
   dirs = []
   dir = dom.getElementsByTagName("Dir")
   for node in dir:
      if node.getAttribute("name") == path:
         print path
         for child_node in node.childNodes:
	    if child_node.nodeType == child_node.ELEMENT_NODE:
               for next_node in child_node.childNodes:
	          if next_node.nodeType == next_node.TEXT_NODE:
                     print next_node.data
                     dirs.append(next_node.data)
   return dirs                

def get_file_node(dom, path):
   files = dom.getElementsByTagName("File")
   for node in files:
      if node.getAttribute("path") == path:
         return node
   print "we have an error"
   raise OSError(ENOENT) # the file is not found in the metadata

if __name__ == "__main__":
    if len(argv) != 3:
        print 'usage: %s <local_storage_path> <mountpoint>' % argv[0]
        exit(1)
    fuse = FUSE(Metadata(argv[1]), argv[2], foreground=True)
