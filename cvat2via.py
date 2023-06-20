import os
import json
from xml.dom import minidom

output_path = 'via_region_data.json'
dict = {}

# read xml file
file = minidom.parse('cvat/annotations.xml')

# serializing json
json_object =json.dumps(dict,indent=4)

# writing to json file
with open(output_path,'w') as f:
    f.write(json_object)
