import sys
import os
import shutil
import json
from xml.dom import minidom

src = sys.argv[1]
dst = 'dst'
if not os.path.exists(dst):
    os.mkdir(dst)
else:
    print('please remove dst first')
    exit(-1)

# all supported annotation types
annotation_types = ['box','polygon','polyline']
dict = {}

if __name__ == "__main__":
    # read xml file
    file = minidom.parse(os.path.join(src,'annotations.xml'))

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
        img_size = os.path.getsize(os.path.join(src,'images',img_name))

        # copy image
        shutil.copy(os.path.join(src,'images',img_name),os.path.join(dst,img_name))

        # create temporary dict
        tmp['filename'] = img_name
        tmp['file_attributes'] = {}
        tmp['size'] = img_size
        tmp['regions'] = []

        # get annotation follow ananotation_types
        for annotation_type in annotation_types:
            annotations = image.getElementsByTagName(annotation_type)
            m = annotations.length
            print('\t\t','Found',m,annotation_type)

            for annotation in annotations:
                # current region
                region = {
                    "shape_attributes":{},
                    "region_attributes": {
                        "labels": ""
                    }
                }
                # get label
                label = annotation.attributes['label'].value
                region["region_attributes"]["labels"]=label

                if annotation_type == "box":
                    region_name = "rect"
                    region['shape_attributes']['name'] = region_name
                    xtl = int(float(annotation.attributes['xtl'].value))
                    ytl = int(float(annotation.attributes['ytl'].value))
                    xbr = int(float(annotation.attributes['xbr'].value))
                    ybr = int(float(annotation.attributes['ybr'].value))
                    width = xbr -xtl
                    height = ybr - ytl
                    region['shape_attributes']['x'] = xtl
                    region['shape_attributes']['y'] = ytl
                    region['shape_attributes']['width'] = width
                    region['shape_attributes']['height'] = height

                elif annotation_type == "polygon":
                    region_name = "polygon"
                    region['shape_attributes']['name'] = region_name
                    region['shape_attributes']['all_points_x'] = []
                    region['shape_attributes']['all_points_y'] = []
                    points = annotation.attributes['points'].value
                    points = points.split(';')
                    for point in points:
                        x,y = point.split(',')
                        region['shape_attributes']['all_points_x'].append(int(float(x)))
                        region['shape_attributes']['all_points_y'].append(int(float(y)))


                elif annotation_type == "polyline":
                    region_name = "polyline"
                    region['shape_attributes']['name'] = region_name
                    region['shape_attributes']['all_points_x'] = []
                    region['shape_attributes']['all_points_y'] = []
                    points = annotation.attributes['points'].value
                    points = points.split(';')
                    for point in points:
                        x,y = point.split(',')
                        region['shape_attributes']['all_points_x'].append(int(float(x)))
                        region['shape_attributes']['all_points_y'].append(int(float(y)))

                else:
                    print("Error:",annotation_type,"is not supported")
                    continue

                # update region
                tmp["regions"].append(region)

        img_key = img_name + str(img_size)
        # update to dictionary
        dict[img_key] = tmp

    # serializing json
    json_object =json.dumps(dict,indent=4)

    # writing to json file
    with open(os.path.join(dst,'via_json_dat.json'),'w') as f:
        f.write(json_object)
        
    print("Done!")

    exit(0)
