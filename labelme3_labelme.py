import os
import sys
import json
import shutil
import base64
from xml.dom import minidom
from PIL import Image

src = sys.argv[1]

dst = 'dst'
if not os.path.exists(dst):
    os.mkdir(dst)
else:
    print('please remove dst first')
    #exit(-1)
    
def xml_to_json(xml_file):
    json_data = {}
    json_data['version'] = '5.2.1'
    json_data['flags'] = {}
    json_data['shapes'] = []
    json_data['imagePath'] = xml_file.split('.')[0]+'.jpg'
    
    # convert image to base64
    with open(os.path.join(src,json_data['imagePath']), "rb") as img_file:
        img_string = base64.b64encode(img_file.read())
        img_string = img_string.decode('utf-8')
    json_data['imageData'] = img_string
    
    # get image shape
    img = Image.open(os.path.join(src,json_data['imagePath']))
    img_width, img_height = img.size
    json_data['imageHeight'] = int(img_height)
    json_data['imageWidth'] = int(img_width)
    
    # read xml file
    file = minidom.parse(os.path.join(src,xml_file))
    
    # use getElementsByTagName() to get tag objects
    objects = file.getElementsByTagName('object')
    
    for object in objects:
        # current shape
        shape = {}
        shape['points'] = []
        shape['group_id'] = None
        shape['description'] = ""
        shape['flags'] = {}
        shape['shape_type'] = "polygon"
        
        # get label
        shape['label'] = object.getElementsByTagName('name')[0].firstChild.data
        
        # get polygon
        polygon = object.getElementsByTagName('polygon')[0]
        pts = polygon.getElementsByTagName('pt')
        for pt in pts:
            x = float(pt.getElementsByTagName('x')[0].firstChild.data)
            y = float(pt.getElementsByTagName('y')[0].firstChild.data)
            point = [x,y]
            shape['points'].append(point)
        
        # append shape to shapes
        json_data['shapes'].append(shape)
    
    return json_data

# collect all xml files
xml_files = []
for file in os.listdir(src):
    if '.xml' in file:
        xml_files.append(file)

print(f'total: {len(xml_files)} xml files')

for xml_file in xml_files:
    print(xml_file)
    # get xml file name
    file_name = xml_file.split('.')[0]
    
    # copy image to destination folder
    shutil.copy(os.path.join(src,file_name+'.jpg'),os.path.join(dst,file_name+'.jpg'))
    
    # convert xml to json
    json_data = xml_to_json(xml_file)
    
    # serializing json
    json_object =json.dumps(json_data,indent=4)
    with open(os.path.join(dst,file_name+'.json'),'w') as f:
        f.write(json_object)
    