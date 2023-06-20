import os
from xml.dom import minidom

root = minidom.Document()

# create tag
xml = root.createElement('root')
root.appendChild(xml)

# set attribute for element
productChild = root.createElement('product')
productChild.setAttribute('name','Geeks for Geeks')
xml.appendChild(productChild)

xml_str = root.toprettyxml(indent='\t')

save_path_file = 'tmp/gfg.xml'

with open(save_path_file,'w') as f:
    f.write(xml_str)
