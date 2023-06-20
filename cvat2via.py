import os
import json
from xml.dom import minidom

output_path = 'via_region_data.json'
# all supported annotation types
annotation_types = ['box','polygon','polyline']
dict = {}

# read xml file
file = minidom.parse('cvat/annotations.xml')

# use getElementsByTagName() to get tag image
images = file.getElementsByTagName('image')
n = images.length
print('Found',n,'images')

for i in range(n):
    tmp = {}
    print('image',i)
    # get i-th image
    image = images[i]
    img_name = image.attributes['name'].value
    img_width = int(image.attributes['width'].value)
    img_height = int(image.attributes['height'].value)
    img_side = int(img_width*img_height/3.8)

    # create temporary dict
    tmp['filename'] = img_name
    tmp['file_attributes'] = {}
    tmp['side'] = img_side
    tmp['regions'] = []

    # get annotation follow ananotation_types
    for annotation_type in annotation_types:
        annotations = image.getElementsByTagName(annotation_type)
        m = annotations.length
        print('\t\t','Found ',m,' ',annotation_type)

    img_key = img_name + str(img_side)
    # update to dictionary
    dict[img_key] = tmp

# serializing json
json_object =json.dumps(dict,indent=4)

# writing to json file
with open(output_path,'w') as f:
    f.write(json_object)
