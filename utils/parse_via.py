import json

# all supported annotation types
annotation_types = ['rect','polygon','polyline']

# read json file
with open('via/via_region_data.json') as f:
    json_data = json.load(f)

# list all images at fist level
images = json_data.keys()
print('Found ',len(images),' images in json file')
for image in images:
    # get current image
    current_image = json_data[image]
    
    # keys =  current_image.keys()
    # for key in keys:
    #     print('\t\t',key,':',current_image[key])
    
    # get regions
    regions = current_image['regions']
    print('\t\tFound ',len(regions),' regions')