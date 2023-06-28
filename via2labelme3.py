import os
import shutil
import json
from xml.dom import minidom
from PIL import Image

src = "dataset/via"
dst = 'dst'
if not os.path.exists(dst):
    os.mkdir(dst)
else:
    print('please remove dst first')
    #exit(-1)

# all via tool supported annotation types
annotation_types = ['rect','polygon']

def gen_xml(img_name,img_width,img_height,regions):
    '''
    function create labelme3.0 format xml file 
    '''
    root = minidom.Document()

    # create annotation tag
    xml = root.createElement('annotation')
    
    # create filename tag
    filename = root.createElement('filename')
    filename.appendChild(root.createTextNode(img_name))
    xml.appendChild(filename)
    
    # create folder tag
    folder = root.createElement('folder')
    folder.appendChild(root.createTextNode(''))
    xml.appendChild(folder)
    
    # create source tag
    source = root.createElement('source')
    sourceImage = root.createElement('sourceImage')
    sourceImage.appendChild(root.createTextNode(''))
    sourceAnnotation = root.createElement('sourceAnnotation')
    sourceAnnotation.appendChild(root.createTextNode('Datumaro'))
    source.appendChild(sourceImage)
    source.appendChild(sourceAnnotation)
    xml.appendChild(source)
    
    # create imagesize tag
    imagesize = root.createElement('imagesize')
    nrows = root.createElement('nrows')
    nrows.appendChild(root.createTextNode(str(img_height)))
    ncols = root.createElement('ncols')
    ncols.appendChild(root.createTextNode(str(img_width)))
    imagesize.appendChild(nrows)
    imagesize.appendChild(ncols)
    xml.appendChild(imagesize)
    
    # loop through all regions
    for region in regions:
        # create object tag
        object = root.createElement('object')
        # get region label
        img_label = region.get('region_attributes').get('labels')
        # create name tag
        name = root.createElement('name')
        name.appendChild(root.createTextNode(img_label))
        object.appendChild(name)
        xml.appendChild(object)
    
    
    # add general annotation tag
    root.appendChild(xml)
    # convert to xml string
    xml_str = root.toprettyxml(indent='\t')
    
    return xml_str
    
# Opening JSON file
with open(os.path.join(src,'via_region_data.json')) as f:
    data = json.load(f) # return json data as dictionary
    
# get all image key in dictionary
img_keys = list(data.keys())

# loop through all elements in dictionary
for img_key in img_keys:
    
    # get current image
    img_dic = data[img_key]
    img_name = img_dic['filename'] # get image name
    
    # get image shape
    img = Image.open(os.path.join(src,img_name))
    img_width, img_height = img.size

    regions = img_dic['regions'] # get regions
    
    # copy image to destination folder
    shutil.copy(os.path.join(src,img_name),os.path.join(dst,img_name))
    
    # generate xml file and save to destination folder
    xml_str = gen_xml(img_name,img_width,img_height,regions)
    save_path_file = os.path.join(dst,img_name.split('.')[0]+'.xml')
    with open(save_path_file,'w') as f:
        f.write(xml_str)
    
    

    
