# python3 via2labelme3.py dataset/via
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
    exit(-1)

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
    for i,region in enumerate(regions):
        # create object tag
        object = root.createElement('object')
        # get region label
        img_label = region.get('region_attributes').get('labels')
        img_type = region.get('shape_attributes').get('name')
        # create name tag
        name = root.createElement('name')
        name.appendChild(root.createTextNode(img_label))
        object.appendChild(name)
        # create deleted tag
        deleted = root.createElement('deleted')
        deleted.appendChild(root.createTextNode('0'))
        object.appendChild(deleted)
        # create verified tag
        verified = root.createElement('verified')
        verified.appendChild(root.createTextNode('0'))
        object.appendChild(verified)
        # create occluded tag
        occluded = root.createElement('occluded')
        occluded.appendChild(root.createTextNode('no'))
        object.appendChild(occluded)
        # create date tag
        date = root.createElement('date')
        date.appendChild(root.createTextNode(''))
        object.appendChild(date)
        # create id tag
        id = root.createElement('id')
        id.appendChild(root.createTextNode(str(i)))
        object.appendChild(id)
        # create parts tag
        parts = root.createElement('parts')
        hasparts = root.createElement('hasparts')
        hasparts.appendChild(root.createTextNode(''))
        ispartof = root.createElement('ispartof')
        ispartof.appendChild(root.createTextNode(''))
        parts.appendChild(hasparts)
        parts.appendChild(ispartof)
        object.appendChild(parts)        
        # create attributes tag and type tag
        if img_type == 'polygon':
            # only create attributes tag
            attributes = root.createElement('attributes')
            attributes.appendChild(root.createTextNode(''))
            object.appendChild(attributes)
        elif img_type == 'rect':
            # create atrributes tag
            attributes = root.createElement('attributes')
            attributes.appendChild(root.createTextNode('rotation=0.0'))
            object.appendChild(attributes)
            # crate type tag
            type = root.createElement('type')
            type.appendChild(root.createTextNode('bounding_box'))
            object.appendChild(type)
        else:
            print('attributes:',img_type, ' is not supported, continue')
            continue
        # create polygon tag
        polygon = root.createElement('polygon')
        username = root.createElement('username')
        username.appendChild(root.createTextNode(''))
        polygon.appendChild(username)
        if img_type == "polygon":
            all_points_x = region.get('shape_attributes').get('all_points_x')
            all_points_y = region.get('shape_attributes').get('all_points_y')
            for j in range(len(all_points_x)):
                # create pt tag
                pt = root.createElement('pt')
                x_tag = root.createElement('x')
                y_tag = root.createElement('y')
                x = all_points_x[j]
                y = all_points_y[j]
                x_tag.appendChild(root.createTextNode(str(int(x))))
                y_tag.appendChild(root.createTextNode(str(int(y))))
                pt.appendChild(x_tag)
                pt.appendChild(y_tag)
                polygon.appendChild(pt)
                
        elif img_type == "rect":
            x = region.get('shape_attributes').get('x')
            y = region.get('shape_attributes').get('y')
            width = region.get('shape_attributes').get('width')
            height = region.get('shape_attributes').get('height')
            # top left point
            pt = root.createElement('pt')
            x_tag = root.createElement('x')
            y_tag = root.createElement('y')
            x_tag.appendChild(root.createTextNode(str(int(x))))
            y_tag.appendChild(root.createTextNode(str(int(y))))
            pt.appendChild(x_tag)
            pt.appendChild(y_tag)
            polygon.appendChild(pt)
            # top right point
            pt = root.createElement('pt')
            x_tag = root.createElement('x')
            y_tag = root.createElement('y')
            x_tag.appendChild(root.createTextNode(str(int(x+width))))
            y_tag.appendChild(root.createTextNode(str(int(y))))
            pt.appendChild(x_tag)
            pt.appendChild(y_tag)
            polygon.appendChild(pt)
            # bottom right point
            pt = root.createElement('pt')
            x_tag = root.createElement('x')
            y_tag = root.createElement('y')
            x_tag.appendChild(root.createTextNode(str(int(x+width))))
            y_tag.appendChild(root.createTextNode(str(int(y+height))))
            pt.appendChild(x_tag)
            pt.appendChild(y_tag)
            polygon.appendChild(pt)
            # bottom left point
            pt = root.createElement('pt')
            x_tag = root.createElement('x')
            y_tag = root.createElement('y')
            x_tag.appendChild(root.createTextNode(str(int(x))))
            y_tag.appendChild(root.createTextNode(str(int(y)+height)))
            pt.appendChild(x_tag)
            pt.appendChild(y_tag)
            polygon.appendChild(pt)
        else:
            print('polygon:',img_type, ' is not supported, continue')
            continue
        object.appendChild(polygon)
            
        # append object to annotation tag
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