"""
Convert Pascal VOC format annotations to COCO format.

Usage:
    python voc_coco.py --input_dir /path/to/voc --output_file /path/to/output.json
"""

import os
import sys
import json
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from PIL import Image

from .utils import ensure_dir


def get_category_id(label, categories):
    """
    Get category ID for a label, creating a new category if it doesn't exist.
    
    Args:
        label (str): The object label
        categories (list): List of categories
        
    Returns:
        int: Category ID
    """
    for category in categories:
        if category["name"] == label:
            return category["id"]
    
    # Create new category
    new_id = len(categories) + 1
    categories.append({
        "id": new_id,
        "name": label,
        "supercategory": "object"
    })
    
    return new_id


def parse_voc_xml(xml_file, categories):
    """
    Parse VOC XML annotation file.
    
    Args:
        xml_file (str): Path to XML file
        categories (list): List of categories
        
    Returns:
        dict: Dictionary with image info and annotations
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get image filename
        filename = root.find("filename").text
        
        # Get image size
        size_elem = root.find("size")
        width = int(size_elem.find("width").text)
        height = int(size_elem.find("height").text)
        
        # Create image info
        image_info = {
            "file_name": filename,
            "height": height,
            "width": width
        }
        
        # Parse annotations
        annotations = []
        for obj in root.findall("object"):
            # Get label
            label = obj.find("name").text
            
            # Skip if no bounding box
            bbox_elem = obj.find("bndbox")
            if bbox_elem is None:
                continue
                
            # Get bounding box
            xmin = float(bbox_elem.find("xmin").text)
            ymin = float(bbox_elem.find("ymin").text)
            xmax = float(bbox_elem.find("xmax").text)
            ymax = float(bbox_elem.find("ymax").text)
            
            # COCO format uses [x, y, width, height]
            width = xmax - xmin
            height = ymax - ymin
            
            # Get category id
            category_id = get_category_id(label, categories)
            
            # Create annotation
            annotation = {
                "bbox": [xmin, ymin, width, height],
                "category_id": category_id,
                "segmentation": [],  # No segmentation in VOC
                "area": width * height,
                "iscrowd": 0
            }
            
            annotations.append(annotation)
            
        return image_info, annotations
        
    except Exception as e:
        print(f"Error parsing {xml_file}: {str(e)}")
        return None, None


def voc_to_coco(input_dir, output_file):
    """
    Convert Pascal VOC format annotations to COCO format.
    
    Args:
        input_dir (str): Directory containing VOC XML files
        output_file (str): Output COCO JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            ensure_dir(output_dir)
            
        print(f"Converting VOC annotations from {input_dir} to COCO format...")
        
        # Find all XML files
        xml_files = [f for f in os.listdir(input_dir) if f.endswith('.xml')]
        
        if not xml_files:
            print(f"No VOC XML files found in {input_dir}")
            return False
            
        print(f"Processing {len(xml_files)} VOC XML files...")
        
        # Initialize COCO structure
        coco_json = {
            "info": {
                "description": "Converted from VOC format",
                "url": "",
                "version": "1.0",
                "year": datetime.now().year,
                "contributor": "2Label",
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "licenses": [
                {
                    "id": 1,
                    "name": "Unknown",
                    "url": ""
                }
            ],
            "categories": [],
            "images": [],
            "annotations": []
        }
        
        image_id = 1
        annotation_id = 1
        
        for xml_file in xml_files:
            xml_path = os.path.join(input_dir, xml_file)
            
            # Parse VOC XML
            image_info, annotations = parse_voc_xml(xml_path, coco_json["categories"])
            
            if image_info is None:
                continue
                
            # Add image id
            image_info["id"] = image_id
            image_info["license"] = 1
            
            # Add to COCO
            coco_json["images"].append(image_info)
            
            # Add annotations
            for annotation in annotations:
                annotation["id"] = annotation_id
                annotation["image_id"] = image_id
                
                coco_json["annotations"].append(annotation)
                annotation_id += 1
                
            image_id += 1
            
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(coco_json, f, indent=2)
            
        print(f"Conversion complete. {len(coco_json['images'])} images and {len(coco_json['annotations'])} annotations converted.")
        print(f"Found {len(coco_json['categories'])} categories: {', '.join([c['name'] for c in coco_json['categories']])}")
        print(f"Results saved to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert Pascal VOC format annotations to COCO format")
    parser.add_argument('--input_dir', required=True, help="Directory containing VOC XML files")
    parser.add_argument('--output_file', required=True, help="Output COCO JSON file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    voc_to_coco(args.input_dir, args.output_file)
