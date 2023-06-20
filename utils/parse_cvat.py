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
        
    for annotation_type in annotation_types:
        tag = image.getElementsByTagName(annotation_type)
        print('\t\t','Found ',tag.length,' ',annotation_type)
        
        