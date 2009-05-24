from xml.dom.minidom import Document, Node

from stat import S_IFDIR
from time import time

def format_metadata(xmlpath):
   dom = Document()
   xml = dom.createElement("xml")
   root = dom.createElement("File")
   now = str(int(time()))
   root.setAttribute("path", "/")
   root.setAttribute("st_mode", str(0777 | S_IFDIR) )
   root.setAttribute("st_ctime", now)
   root.setAttribute("st_mtime", now)
   root.setAttribute("st_atime", now)

   xml.appendChild(root)
   dom.appendChild(xml)

   fp = open(xmlpath, "w")
   dom.writexml(fp, newl="\n")
   fp.close()

