from xml.dom import minidom

# all supported annotation types
annotation_types = ['box','polygon','polyline']

# parse xml file
file = minidom.parse('cvat/annotations.xml')

# use getElementsByTagName() to get tag image
images = file.getElementsByTagName('image')
n = images.length
print('Found ',n,' images')

for i in range(n):
    
    # get i-th image
    image = images[i]
    print('image',i)
    
    # get all keys attribute of image
    for a in image.attributes.keys():
        print('\t',a,'=',image.attributes[a].value)
        
    # get annotation follow ananotation_types
    for annotation_type in annotation_types:
        annotations = image.getElementsByTagName(annotation_type)
        m = annotations.length
        print('\t\t','Found ',m,' ',annotation_type)
        
        # get all keys attribute of annotation
        for j in range(m):
            annotation = annotations[j]
            # get all keys attribute of image
            for a in annotation.attributes.keys():
                print('\t\t\t',a,'=',annotation.attributes[a].value)
        
            
        