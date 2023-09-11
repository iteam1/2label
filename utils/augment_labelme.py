'''
python3 utils/augment_labelme.py --src_path src --no_sample 600
'''
import os
import argparse

# init argument parser
parser = argparse.ArgumentParser(description="labelme dataset augmentation tool")
# add argument to parser
parser.add_argument('--src_path',type = str, help = 'directory of labelme dataset', required = True)
parser.add_argument('--dst_path',type= str, help = 'directory of destination folder', default='dst')
parser.add_argument('--no_sample',type = int,help = 'The number of augmented sample',default = 1000)
parser.add_argument('--ignore_dst',action = 'store_true',help = 'ignore destination folder if exists')
# create arguments
args = parser.parse_args()

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