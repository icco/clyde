from errno import ENOENT, ENOTDIR
from stat import S_IFREG, S_IFDIR
from xml.dom.minidom import parse
from xml.dom.minidom import Document

file_defaults = {}

file_defaults = dict( st_mode=(S_IFREG | 0755), st_atime=23, st_ctime=3, st_mtime=3 )
file_attributes = ('st_atime', 'st_mtime', 'st_ctime', 'st_mode')


class Metadata():
   def __init__(self, xmlpath):
      self.xmlpath = xmlpath

   
   def getattr(self, path):
      """ 
         return a dict containing file information of remote metadata
         raise an exception if the item is not found
      """
      print "*****getattr*******"
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
      print "*******readdir**********"
      return get_dir_names(dom, path)

   def create(self, path):
      print("****create****")
      fp = open("metadata2.xml", "w")
      dom = parse("metadata2.xml")
      new_element = dom.createElement("File")
      new_element.setAttribute("path", path)
      new_element.setAttribute("st_ctime", "0")
      new_element.setAttribute("st_atime", "0")
      dom.appendChild(new_element)
      dom.writexml(fp)
      fp.close()


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
   print dirs
   return dirs                

def get_file_node(dom, path):
   files = dom.getElementsByTagName("File")
   print "***path***"
   print path
   for node in files:
      if node.getAttribute("path") == path:

         return node
   print "we have an error"
   raise OSError(ENOENT) # the file is not found in the metadata



def read(self, path):
   print "in read"
