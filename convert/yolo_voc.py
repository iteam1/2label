'''
python3 convert/yolo_voc.py datasets/phones/src
'''
import os
import sys
import xml.etree.ElementTree as ET
from PIL import Image

# Initialize
labels_path = sys.argv[1] # labels folder
dst = "dst" # destination folder

def convert_yolo_to_voc(yolo_path, voc_path, classes):
    '''
    # Function to convert YOLO format to VOC format
    '''
    # Create VOC directory if it doesn't exist
    if not os.path.exists(voc_path):
        os.makedirs(voc_path)

    for filename in os.listdir(yolo_path):
        if filename.endswith('.txt'):
            yolo_file = os.path.join(yolo_path, filename)
            voc_filename = filename.replace('.txt', '.xml')
            voc_file = os.path.join(voc_path, voc_filename)

            with open(yolo_file, 'r') as yolo:
                root = ET.Element("annotation")
                folder = ET.SubElement(root, "folder")
                folder.text = yolo_path

                filename_element = ET.SubElement(root, "filename")
                filename_element.text = voc_filename.replace('.xml', '')

                size = ET.SubElement(root, "size")
                width_element = ET.SubElement(size, "width")
                height_element = ET.SubElement(size, "height")

                image = Image.open(os.path.join(yolo_path, voc_filename.replace('.xml', '.jpg')))
                width, height = image.size

                width_element.text = str(width)
                height_element.text = str(height)

                for line in yolo:
                    line = line.strip().split()
                    class_id, x_center, y_center, box_width, box_height = map(float, line)

                    object_element = ET.SubElement(root, "object")
                    name = ET.SubElement(object_element, "name")
                    name.text = classes[int(class_id)]
                    bndbox = ET.SubElement(object_element, "bndbox")

                    x_min = (x_center - box_width / 2) * width
                    x_max = (x_center + box_width / 2) * width
                    y_min = (y_center - box_height / 2) * height
                    y_max = (y_center + box_height / 2) * height

                    xmin = ET.SubElement(bndbox, "xmin")
                    ymin = ET.SubElement(bndbox, "ymin")
                    xmax = ET.SubElement(bndbox, "xmax")
                    ymax = ET.SubElement(bndbox, "ymax")

                    xmin.text = str(int(x_min))
                    ymin.text = str(int(y_min))
                    xmax.text = str(int(x_max))
                    ymax.text = str(int(y_max))

                tree = ET.ElementTree(root)
                tree.write(voc_file)

if __name__ == "__main__":
    
    print('Start converting YOLO to VOC')
    
    # Create destination folder
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    # Converting
    # Set your YOLO and VOC directory paths and class names
    yolo_directory =  labels_path # path_to_yolo_data
    voc_directory = dst # path_to_voc_data
    class_names = ["class1", "class2", "class3"]  # Modify with your class names

    convert_yolo_to_voc(yolo_directory, voc_directory, class_names)
