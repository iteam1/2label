"""
Convert CVAT XML format to VIA JSON format.

Usage:
    python cvat_via.py --input_dir /path/to/cvat --output_dir /path/to/output
"""

import os
import sys
import json
import argparse
import shutil
from xml.dom import minidom
from pathlib import Path

from .utils import ensure_dir, clean_dir


def cvat_to_via(input_dir, output_dir="dst"):
    """
    Convert CVAT XML format to VIA JSON format.
    
    Args:
        input_dir (str): Directory containing CVAT XML annotations.xml file and images
        output_dir (str, optional): Output directory for VIA files. Defaults to "dst".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory
        if not clean_dir(output_dir):
            print(f"Failed to create or clean output directory {output_dir}")
            return False
            
        # Define supported annotation types
        annotation_types = ['box', 'polygon', 'polyline']
        
        # Initialize VIA project data
        via_project = {}
        
        # Parse CVAT XML file
        xml_path = os.path.join(input_dir, 'annotations.xml')
        if not os.path.exists(xml_path):
            print(f"CVAT annotations file not found at {xml_path}")
            return False
            
        try:
            xml_doc = minidom.parse(xml_path)
        except Exception as e:
            print(f"Failed to parse XML file {xml_path}: {str(e)}")
            return False
            
        # Get all images from XML
        images = xml_doc.getElementsByTagName('image')
        num_images = images.length
        
        if num_images == 0:
            print("No images found in the CVAT XML file")
            return False
            
        print(f"Found {num_images} images in CVAT XML file")
        
        # Process each image
        for i, image in enumerate(images):
            print(f"Processing image {i+1}/{num_images}")
            
            # Get image filename
            image_name = image.getAttribute('name')
            if not image_name:
                print(f"Warning: Image at index {i} has no name attribute. Skipping.")
                continue
                
            # Get image dimensions
            image_width = int(image.getAttribute('width'))
            image_height = int(image.getAttribute('height'))
            
            # Create VIA image entry
            image_key = f"{i}_{image_name}"
            via_project[image_key] = {
                "filename": image_name,
                "size": -1,  # Will be updated when copying the file
                "regions": [],
                "file_attributes": {}
            }
            
            # Copy image file if it exists
            src_image_path = os.path.join(input_dir, image_name)
            if os.path.exists(src_image_path):
                dst_image_path = os.path.join(output_dir, image_name)
                try:
                    file_size = Path(src_image_path).stat().st_size
                    Path(src_image_path).copy(dst_image_path)
                    via_project[image_key]["size"] = file_size
                except Exception as e:
                    print(f"Warning: Failed to copy image {src_image_path}: {str(e)}")
            else:
                print(f"Warning: Image file {src_image_path} not found")
            
            # Process annotations
            for annotation_type in annotation_types:
                annotations = image.getElementsByTagName(annotation_type)
                
                for j, annotation in enumerate(annotations):
                    # Get label
                    label = annotation.getAttribute('label')
                    
                    region = {
                        "shape_attributes": {},
                        "region_attributes": {
                            "label": label
                        }
                    }
                    
                    # Handle different annotation types
                    if annotation_type == 'box':
                        # Get box coordinates
                        xtl = float(annotation.getAttribute('xtl'))
                        ytl = float(annotation.getAttribute('ytl'))
                        xbr = float(annotation.getAttribute('xbr'))
                        ybr = float(annotation.getAttribute('ybr'))
                        
                        # Convert to VIA format (x, y, width, height)
                        x = xtl
                        y = ytl
                        width = xbr - xtl
                        height = ybr - ytl
                        
                        region["shape_attributes"] = {
                            "name": "rect",
                            "x": x,
                            "y": y,
                            "width": width,
                            "height": height
                        }
                    
                    elif annotation_type in ['polygon', 'polyline']:
                        # Get points
                        points_str = annotation.getAttribute('points')
                        points = []
                        
                        for point_str in points_str.split(';'):
                            if ',' in point_str:
                                x, y = point_str.split(',')
                                points.append([float(x), float(y)])
                        
                        # Convert to VIA format
                        all_x = [p[0] for p in points]
                        all_y = [p[1] for p in points]
                        
                        region["shape_attributes"] = {
                            "name": "polygon" if annotation_type == "polygon" else "polyline",
                            "all_points_x": all_x,
                            "all_points_y": all_y
                        }
                    
                    # Add region to image regions
                    via_project[image_key]["regions"].append(region)
        
        # Save VIA project file
        via_project_path = os.path.join(output_dir, 'via_region_data.json')
        try:
            with open(via_project_path, 'w') as f:
                json.dump(via_project, f, indent=2)
            print(f"VIA project saved to {via_project_path}")
        except Exception as e:
            print(f"Failed to save VIA project: {str(e)}")
            return False
        
        print(f"Conversion complete. Results saved to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert CVAT XML format to VIA JSON format")
    parser.add_argument('--input_dir', required=True, help="Directory containing CVAT annotations.xml file")
    parser.add_argument('--output_dir', default="dst", help="Output directory for VIA files")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cvat_to_via(args.input_dir, args.output_dir)
