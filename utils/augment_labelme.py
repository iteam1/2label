'''
python3 utils/augment_labelme.py --src_path src --no_sample 600 --ignore_dst
'''
import os
import cv2
import json
import random
import argparse
import numpy as np
from tqdm import tqdm
import base64

# argument parser
parser = argparse.ArgumentParser(description="labelme dataset augmentation tool")
# add argument to parser
parser.add_argument('--src_path',type = str, help = 'directory of labelme dataset', required = True)
parser.add_argument('--dst_path',type= str, help = 'directory of destination folder', default='dst')
parser.add_argument('--no_sample',type = int,help = 'The number of augmented sample',default = 1000)
parser.add_argument('--ignore_dst',action = 'store_true',help = 'ignore destination folder if exists')
# create arguments
args = parser.parse_args()

# initialize
#aug_options = ['h_flip','v_flip','rotate','blur','noise','crop','resize','color','brightness','contrast','gamma','hue','saturation','value']
aug_options = ['v_flip']

def flip_point(point, flip_code, image_shape):
    x, y = point
    h, w = image_shape

    if flip_code == 1:  # Horizontal Flip
        new_x = w - x
        new_y = y
    elif flip_code == 0:  # Vertical Flip
        new_x = x
        new_y = h - y
    elif flip_code == -1:  # Both Horizontal and Vertical Flip
        new_x = w - x
        new_y = h - y
    else:
        raise ValueError("Invalid flip_code. Use 0 for vertical, 1 for horizontal, or -1 for both.")

    return new_x, new_y

# define augmentation functions
def h_flip(image,shapes):
    h,w,c = image.shape
    image_aug = image.copy()
    image_aug = cv2.flip(image,0) # horizontal flip
    shapes_aug = shapes.copy()
    for k,shape in enumerate(shapes):
        points = shape['points']
        new_points = []
        for point in points:
            new_x, new_y = flip_point(point, 0, (h, w))
            new_points.append([new_x,new_y])
        shapes_aug[k]['points'] = new_points
    return image_aug,shapes_aug

def v_flip(image,shapes):
    h,w,c = image.shape
    image_aug = image.copy()
    image_aug = cv2.flip(image_aug,1) # veritcal flip
    shapes_aug = shapes.copy()
    for k,shape in enumerate(shapes):
        points = shape['points']
        new_points = []
        for point in points:
            new_x, new_y = flip_point(point, 1, (h, w))
            new_points.append([new_x,new_y])
        shapes_aug[k]['points'] = new_points
    return image_aug,shapes_aug

def noise(image,shapes):
    image_aug = image.copy()
    return image_aug,shapes

if __name__ == "__main__":
    print('labelme dataset augmentation tool, Number of sample = {}'.format(args.no_sample))
    
    # create destination folder
    if not os.path.exists(args.dst_path):
        os.makedirs(args.dst_path)
        print('create destination folder: {}'.format(args.dst_path))
    else:
        if not args.ignore_dst:
            print('Error: destination folder already exists: {}, please remove destination folder before augmentation'.format(args.dst_path))
            exit(-1)
    
    # check source folder
    if not os.path.exists(args.src_path):
        print('Error: source folder not exists: {}'.format(args.src_path))
        exit(-1)
    
    # read source folder
    src_files = os.listdir(args.src_path)
    print('Total files: {}'.format(len(src_files)))
    if len(src_files)%2 != 0:
        print('Error: number of files {} is not even'.format(len(src_files)))
        exit(-1)

    # count annotation files
    annotation_files = []
    for file in src_files:
        if file.endswith('.json'):
            annotation_files.append(file)
    print('Total annotation files: {}'.format(len(annotation_files)))
    
    # check annotation files number
    if len(annotation_files) != len(src_files)/2:
        print('Error: number of annotation files {} is not equal to number of image files {}'.format(len(annotation_files),len(src_files)/2))
        exit(-1)
    
    # trim annotation files if necessary
    if len(annotation_files) > args.no_sample:
        annotation_files = annotation_files[:args.no_sample]
        print('Trim annotation files to {}'.format(len(annotation_files)))
        
    # calculate augmented times of each image
    augmented_times = int(args.no_sample/len(annotation_files))
    print('Augmented times of each image: {}'.format(augmented_times))
        
    # loop for each annotation file
    for annotation_file in tqdm(annotation_files):
        annotation_path = os.path.join(args.src_path,annotation_file)
        
        # read annotation file
        with open(annotation_path,'r') as f:
            annotation = json.load(f)

        # read image
        image_path = os.path.join(args.src_path,annotation['imagePath'])
        image = cv2.imread(image_path)
        image_org = image.copy()
        # get shape of annotations
        shapes = annotation['shapes']
        shapes_org = shapes.copy()
            
        # start augmentation
        for i in range(augmented_times):
            
            # random choose augmentation option
            aug_option = 'v_flip' # random.choice(aug_options)
    
            if aug_option == 'h_flip':
                image_aug,shapes_aug = h_flip(image_org,shapes_org)

            elif aug_option == 'v_flip':
                image_aug,shapes_aug = v_flip(image_org,shapes_org)

            elif aug_option == 'noise':
                image_aug,shapes_aug = noise(image_org,shapes_org)

            # convert image to base64
            retval, buffer = cv2.imencode('.jpg', image_aug)
            jpg_as_text = base64.b64encode(buffer)

            aug_annotation = annotation.copy()
            aug_annotation['imageData'] = jpg_as_text.decode('utf-8')
            aug_annotation['shapes'] = shapes_aug # clear shapes
            aug_annotation['imagePath'] = os.path.splitext(annotation['imagePath'])[0] + '_aug_{}.jpg'.format(i)
            
            # export augmented image and annotation file
            cv2.imwrite(os.path.join(args.dst_path,aug_annotation['imagePath']),image_aug)
            with open(os.path.join(args.dst_path,os.path.splitext(annotation_file)[0] + '_aug_{}.json'.format(i)),'w') as f:
                json.dump(aug_annotation,f)
    
    print('Augmentation done!')