"""
Convert LabelMe 3.0 (XML) format to LabelMe format.

Usage:
    python labelme3_labelme.py --input_dir /path/to/labelme3 --output_dir /path/to/output
"""

import os
import sys
import json
import argparse
import base64
from xml.dom import minidom
from PIL import Image
from pathlib import Path

from .utils import ensure_dir, clean_dir, get_image_dimensions, image_to_base64


def xml_to_json(xml_path, image_path):
    """
    Convert a LabelMe 3.0 XML file to LabelMe JSON format.
    
    Args:
        xml_path (str): Path to the XML file
        image_path (str): Path to the corresponding image file
        
    Returns:
        dict: LabelMe format JSON data
    """
    try:
        # Initialize JSON structure
        json_data = {
            'version': '5.2.1',
            'flags': {},
            'shapes': [],
            'imagePath': os.path.basename(image_path)
        }
        
        # Convert image to base64
        try:
            json_data['imageData'] = image_to_base64(image_path)
        except Exception as e:
            print(f"Warning: Failed to encode image {image_path}: {str(e)}")
            json_data['imageData'] = None
        
        # Get image dimensions
        try:
            width, height = get_image_dimensions(image_path)
            json_data['imageWidth'] = width
            json_data['imageHeight'] = height
        except Exception as e:
            print(f"Warning: Failed to get dimensions for {image_path}: {str(e)}")
            json_data['imageWidth'] = 0
            json_data['imageHeight'] = 0
        
        # Parse XML file
        try:
            xml_doc = minidom.parse(xml_path)
            
            # Extract objects
            objects = xml_doc.getElementsByTagName('object')
            
            for obj in objects:
                # Current shape
                shape = {
                    'label': obj.getElementsByTagName('name')[0].firstChild.data,
                    'points': [],
                    'group_id': None,
                    'shape_type': 'polygon',
                    'flags': {}
                }
                
                # Get polygon points
                polygon = obj.getElementsByTagName('polygon')[0]
                pts = polygon.getElementsByTagName('pt')
                
                for pt in pts:
                    x = float(pt.getElementsByTagName('x')[0].firstChild.data)
                    y = float(pt.getElementsByTagName('y')[0].firstChild.data)
                    shape['points'].append([x, y])
                
                # Add shape to shapes list
                json_data['shapes'].append(shape)
            
            return json_data
            
        except Exception as e:
            print(f"Error parsing XML file {xml_path}: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Error processing file {xml_path}: {str(e)}")
        return None


def labelme3_to_labelme(input_dir, output_dir="dst"):
    """
    Convert all LabelMe 3.0 XML files in a directory to LabelMe JSON format.
    
    Args:
        input_dir (str): Directory containing LabelMe 3.0 XML files
        output_dir (str, optional): Output directory for LabelMe files. Defaults to "dst".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directories
        output_images_dir = os.path.join(output_dir, 'images')
        output_annotations_dir = os.path.join(output_dir, 'annotations')
        
        clean_dir(output_dir)
        ensure_dir(output_images_dir)
        ensure_dir(output_annotations_dir)
        
        # Find all XML files
        xml_files = [f for f in os.listdir(input_dir) if f.endswith('.xml')]
        
        if not xml_files:
            print(f"No XML files found in {input_dir}")
            return False
            
        print(f"Converting {len(xml_files)} LabelMe 3.0 XML files to LabelMe format...")
        
        for xml_file in xml_files:
            base_name = os.path.splitext(xml_file)[0]
            image_file = f"{base_name}.jpg"  # Assuming JPG format
            
            # Check if image exists
            image_path = os.path.join(input_dir, image_file)
            if not os.path.exists(image_path):
                print(f"Warning: Image file {image_file} not found. Skipping {xml_file}.")
                continue
                
            # Convert XML to JSON
            xml_path = os.path.join(input_dir, xml_file)
            json_data = xml_to_json(xml_path, image_path)
            
            if json_data:
                # Save JSON file
                json_path = os.path.join(output_annotations_dir, f"{base_name}.json")
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=2)
                    
                # Copy image file
                dst_image_path = os.path.join(output_images_dir, image_file)
                try:
                    Path(image_path).copy(dst_image_path)
                except Exception as e:
                    print(f"Error copying image {image_path}: {str(e)}")
        
        print(f"Conversion complete. Results saved to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert LabelMe 3.0 XML files to LabelMe JSON format")
    parser.add_argument('--input_dir', required=True, help="Directory containing LabelMe 3.0 XML files")
    parser.add_argument('--output_dir', default="dst", help="Output directory for LabelMe files")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    labelme3_to_labelme(args.input_dir, args.output_dir)