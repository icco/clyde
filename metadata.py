from errno import ENOENT, ENOTDIR
from stat import S_IFREG, S_IFDIR
from xml.dom.minidom import parse
from xml.dom.minidom import Document

file_defaults = {}

file_defaults = dict( st_mode=(S_IFREG | 0755), st_atime=0, st_ctime=0, st_mtime=0, st_gid=0, st_nlink=3, st_size=4096, st_uid=0)
file_attributes = ('st_atime', 'st_ctime','st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid')

class Metadata():
   def __init__(self, xmlpath):
      self.xmlpath = xmlpath

   def getattr(self, path):
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

   def readdir(self, path):
      dom = parse(self.xmlpath)
      return get_dir_names(dom, path)

   def create(self, path):
      print("****create****")
      
      # prepare File element to be put in metadata
      dom = parse("metadata.xml")
      root = dom.documentElement
      new_element = dom.createElement("File")
      new_element.setAttribute("path", path)
      new_element.setAttribute("st_ctime", "0")
      new_element.setAttribute("st_atime", "0")
      root.appendChild(new_element)

      #prepare Dir element to put new file
      new_element_readdir = dom.createElement("file")
      tuple1 = path.rpartition("/")
      file_name = tuple1[2]
      text_node = dom.createTextNode(file_name)
      new_element_readdir.appendChild(text_node)
      dir = dom.getElementsByTagName("Dir")
      tuple = path.rpartition("/")
      dir_name = tuple[0]
      print dir_name
      for node in dir:
          if node.getAttribute("name") == dir_name:
              node.appendChild(new_element_readdir)
      
      fp = open("metadata.xml", "w")
      dom.writexml(fp)
      fp.close()

   def isLocal(self, path):
      flag = False
      dom = parse(self.xmlpath)
      files = dom.getElementsByTagName("File")
      for node in files:
         print (node.getAttribute("node"), node.getAttribute("path"), path)
         if (node.getAttribute("path") == path) and (node.getAttribute("node") == '2'):
            flag = True
            break
      print flag
      return flag

   def isDir(self, path):
      flag = False
      dom = parse(self.xmlpath)
      files = dom.getElementsByTagName("File")
      for node in files:
         print (node.getAttribute("node"), node.getAttribute("st_mode"), path)
         if (node.getAttribute("st_mode") == '16384') and (node.getAttribute("node") == '2'):
            flag = True
            break
      print flag
      return flag

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
   print ("DIRS ",dirs)
   return dirs                

def get_file_node(dom, path):
   files = dom.getElementsByTagName("File")
   print path
   for node in files:
      if node.getAttribute("path") == path:
         return node
   print "we have an error"
   raise OSError(ENOENT) # the file is not found in the metadata



def read(self, path):
   print "in read"
