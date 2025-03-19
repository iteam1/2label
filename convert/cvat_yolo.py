"""
Convert CVAT format annotations to YOLO format.

Usage:
    python cvat_yolo.py --input_dir /path/to/cvat --output_dir /path/to/output
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import shutil

from .utils import ensure_dir, clean_dir


def parse_cvat_xml(xml_file):
    """
    Parse CVAT XML annotation file.
    
    Args:
        xml_file (str): Path to CVAT XML file
        
    Returns:
        tuple: (image_info, class_list, annotations) or (None, None, None) if error
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get all classes/labels
        labels = []
        for label in root.findall('.//label'):
            name_elem = label.find('name')
            if name_elem is not None:
                labels.append(name_elem.text)
                
        if not labels:
            print(f"No labels found in {xml_file}")
            return None, None, None
            
        # Get images and annotations
        images = {}
        
        for image_elem in root.findall('.//image'):
            image_name = image_elem.get('name')
            if not image_name:
                continue
                
            width = float(image_elem.get('width', 0))
            height = float(image_elem.get('height', 0))
            
            if width <= 0 or height <= 0:
                print(f"Warning: Invalid dimensions for image {image_name}")
                continue
                
            images[image_name] = {
                'width': width,
                'height': height,
                'annotations': []
            }
            
            # Get annotations for this image
            for box in image_elem.findall('.//box'):
                label = box.get('label')
                if label not in labels:
                    print(f"Warning: Label {label} not in label list")
                    continue
                    
                label_id = labels.index(label)
                
                xtl = float(box.get('xtl', 0))
                ytl = float(box.get('ytl', 0))
                xbr = float(box.get('xbr', 0))
                ybr = float(box.get('ybr', 0))
                
                # Convert to YOLO format (normalized center, width, height)
                x_center = (xtl + xbr) / (2 * width)
                y_center = (ytl + ybr) / (2 * height)
                box_width = (xbr - xtl) / width
                box_height = (ybr - ytl) / height
                
                # Validate coordinates
                if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 
                        0 <= box_width <= 1 and 0 <= box_height <= 1):
                    print(f"Warning: Invalid box coordinates for {image_name}, label {label}")
                    continue
                
                images[image_name]['annotations'].append({
                    'label_id': label_id,
                    'x_center': x_center,
                    'y_center': y_center,
                    'width': box_width,
                    'height': box_height
                })
                
        return images, labels, True
        
    except Exception as e:
        print(f"Error parsing CVAT XML file {xml_file}: {str(e)}")
        return None, None, None


def write_yolo_files(images, labels, input_dir, output_dir):
    """
    Write YOLO annotation files and copy images.
    
    Args:
        images (dict): Image information and annotations
        labels (list): List of class names
        input_dir (str): Input directory containing images
        output_dir (str): Output directory for YOLO format
        
    Returns:
        tuple: (processed_count, total_count)
    """
    try:
        # Write classes.txt
        with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
            f.write('\n'.join(labels))
            
        processed_count = 0
        for image_name, image_info in images.items():
            # Find image file
            image_path = None
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                test_path = os.path.join(input_dir, image_name)
                if os.path.exists(test_path):
                    image_path = test_path
                    break
                    
            if not image_path:
                print(f"Warning: Image {image_name} not found in {input_dir}")
                continue
                
            # Copy image to output directory
            output_image_path = os.path.join(output_dir, image_name)
            try:
                shutil.copy2(image_path, output_image_path)
            except Exception as e:
                print(f"Error copying image {image_path}: {str(e)}")
                continue
                
            # Write YOLO annotation
            base_name = os.path.splitext(image_name)[0]
            txt_path = os.path.join(output_dir, f"{base_name}.txt")
            
            with open(txt_path, 'w') as f:
                for ann in image_info['annotations']:
                    # YOLO format: class_id center_x center_y width height
                    f.write(f"{ann['label_id']} {ann['x_center']:.6f} "
                           f"{ann['y_center']:.6f} {ann['width']:.6f} "
                           f"{ann['height']:.6f}\n")
                    
            processed_count += 1
            
        return processed_count, len(images)
        
    except Exception as e:
        print(f"Error writing YOLO files: {str(e)}")
        return 0, len(images)


def cvat_to_yolo(input_dir, output_dir="dst"):
    """
    Convert CVAT format annotations to YOLO format.
    
    Args:
        input_dir (str): Directory containing CVAT XML file and images
        output_dir (str, optional): Output directory for YOLO files. Defaults to "dst".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory
        if not clean_dir(output_dir):
            print(f"Failed to create output directory {output_dir}")
            return False
            
        print(f"Converting CVAT annotations from {input_dir} to YOLO format...")
        
        # Find CVAT XML file
        xml_files = [f for f in os.listdir(input_dir) if f.endswith('.xml')]
        
        if not xml_files:
            print(f"No CVAT XML files found in {input_dir}")
            return False
            
        # Use the first XML file found
        xml_file = os.path.join(input_dir, xml_files[0])
        print(f"Using CVAT file: {xml_file}")
        
        # Parse CVAT XML
        images, labels, success = parse_cvat_xml(xml_file)
        
        if not success or not images or not labels:
            print(f"Failed to parse CVAT file {xml_file}")
            return False
            
        print(f"Found {len(images)} images and {len(labels)} classes")
        print(f"Classes: {', '.join(labels)}")
        
        # Write YOLO files
        processed_count, total_count = write_yolo_files(images, labels, input_dir, output_dir)
        
        print(f"Conversion complete. {processed_count}/{total_count} images converted to YOLO format.")
        print(f"Results saved to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert CVAT format annotations to YOLO format")
    parser.add_argument('--input_dir', required=True, help="Directory containing CVAT XML file and images")
    parser.add_argument('--output_dir', default="dst", help="Output directory for YOLO files")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cvat_to_yolo(args.input_dir, args.output_dir)
