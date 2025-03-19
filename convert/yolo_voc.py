"""
Convert YOLO format annotations to Pascal VOC format.

Usage:
    python yolo_voc.py --input_dir /path/to/yolo --output_dir /path/to/output
"""

import os
import sys
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

from .utils import ensure_dir, clean_dir


def create_voc_xml(image_path, txt_path, class_names, output_path):
    """
    Create a Pascal VOC format XML file from YOLO annotations.
    
    Args:
        image_path (str): Path to the image file
        txt_path (str): Path to the YOLO annotation text file
        class_names (list): List of class names
        output_path (str): Path to save the output XML file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get image dimensions
        with Image.open(image_path) as img:
            width, height = img.size
            
        # Create XML structure
        root = ET.Element("annotation")
        
        # Add folder and filename
        folder = ET.SubElement(root, "folder")
        folder.text = os.path.basename(os.path.dirname(image_path))
        
        filename = ET.SubElement(root, "filename")
        filename.text = os.path.basename(image_path)
        
        path = ET.SubElement(root, "path")
        path.text = image_path
        
        # Add source information
        source = ET.SubElement(root, "source")
        database = ET.SubElement(source, "database")
        database.text = "YOLO to VOC Converter"
        
        # Add size information
        size = ET.SubElement(root, "size")
        width_elem = ET.SubElement(size, "width")
        width_elem.text = str(width)
        height_elem = ET.SubElement(size, "height")
        height_elem.text = str(height)
        depth = ET.SubElement(size, "depth")
        depth.text = "3"  # Assuming RGB images
        
        # Add segmented information
        segmented = ET.SubElement(root, "segmented")
        segmented.text = "0"
        
        # Parse YOLO annotation file
        with open(txt_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                # YOLO format: class_id center_x center_y width height
                class_id = int(parts[0])
                center_x = float(parts[1])
                center_y = float(parts[2])
                box_width = float(parts[3])
                box_height = float(parts[4])
                
                # Convert normalized coordinates to absolute coordinates
                x_min = int((center_x - box_width / 2) * width)
                y_min = int((center_y - box_height / 2) * height)
                x_max = int((center_x + box_width / 2) * width)
                y_max = int((center_y + box_height / 2) * height)
                
                # Ensure coordinates are within image boundaries
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(width, x_max)
                y_max = min(height, y_max)
                
                # Create object element
                obj = ET.SubElement(root, "object")
                
                # Add name (class)
                name = ET.SubElement(obj, "name")
                if class_id < len(class_names):
                    name.text = class_names[class_id]
                else:
                    name.text = f"class_{class_id}"
                    
                # Add pose
                pose = ET.SubElement(obj, "pose")
                pose.text = "Unspecified"
                
                # Add truncated
                truncated = ET.SubElement(obj, "truncated")
                truncated.text = "0"
                
                # Add difficult
                difficult = ET.SubElement(obj, "difficult")
                difficult.text = "0"
                
                # Add bounding box
                bndbox = ET.SubElement(obj, "bndbox")
                
                xmin = ET.SubElement(bndbox, "xmin")
                xmin.text = str(x_min)
                
                ymin = ET.SubElement(bndbox, "ymin")
                ymin.text = str(y_min)
                
                xmax = ET.SubElement(bndbox, "xmax")
                xmax.text = str(x_max)
                
                ymax = ET.SubElement(bndbox, "ymax")
                ymax.text = str(y_max)
        
        # Write XML to file
        tree = ET.ElementTree(root)
        tree.write(output_path)
        
        return True
        
    except Exception as e:
        print(f"Error creating VOC XML for {image_path}: {str(e)}")
        return False


def yolo_to_voc(input_dir, output_dir="dst"):
    """
    Convert YOLO format annotations to Pascal VOC format.
    
    Args:
        input_dir (str): Directory containing YOLO annotations and images
        output_dir (str, optional): Output directory for VOC annotations. Defaults to "dst".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory
        if not clean_dir(output_dir):
            print(f"Failed to create output directory {output_dir}")
            return False
            
        print(f"Converting YOLO annotations from {input_dir} to VOC format...")
        
        # Check for classes.txt file
        classes_file = os.path.join(input_dir, 'classes.txt')
        class_names = []
        
        if os.path.exists(classes_file):
            with open(classes_file, 'r') as f:
                class_names = [line.strip() for line in f.readlines()]
            print(f"Found {len(class_names)} classes in classes.txt")
        else:
            print("Warning: classes.txt not found. Class names will be generated automatically.")
            
        # Find all YOLO annotation files (txt)
        txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt') and f != 'classes.txt']
        
        if not txt_files:
            print(f"No YOLO annotation files found in {input_dir}")
            return False
            
        print(f"Processing {len(txt_files)} YOLO annotation files...")
        
        converted_count = 0
        for txt_file in txt_files:
            # Get base filename
            base_name = os.path.splitext(txt_file)[0]
            
            # Find corresponding image file
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            image_path = None
            
            for ext in image_extensions:
                img_file = f"{base_name}{ext}"
                img_path = os.path.join(input_dir, img_file)
                if os.path.exists(img_path):
                    image_path = img_path
                    break
                    
            if not image_path:
                print(f"Warning: No image found for {txt_file}. Skipping.")
                continue
                
            # Create VOC XML file
            txt_path = os.path.join(input_dir, txt_file)
            xml_output_path = os.path.join(output_dir, f"{base_name}.xml")
            
            success = create_voc_xml(image_path, txt_path, class_names, xml_output_path)
            
            if success:
                # Copy image file
                output_img_path = os.path.join(output_dir, os.path.basename(image_path))
                try:
                    Path(image_path).copy(output_img_path)
                    converted_count += 1
                except Exception as e:
                    print(f"Error copying image {image_path}: {str(e)}")
        
        print(f"Conversion complete. {converted_count} annotations converted to VOC format.")
        print(f"Results saved to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert YOLO format annotations to Pascal VOC format")
    parser.add_argument('--input_dir', required=True, help="Directory containing YOLO annotations and images")
    parser.add_argument('--output_dir', default="dst", help="Output directory for VOC annotations")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    yolo_to_voc(args.input_dir, args.output_dir)
