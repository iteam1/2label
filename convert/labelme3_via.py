"""
Convert LabelMe 3.0 (XML) format annotations to VIA (JSON) format.

Usage:
    python labelme3_via.py --input_dir /path/to/labelme3 --output_dir /path/to/output
"""

import os
import sys
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

from .utils import ensure_dir, clean_dir


def get_image_size_from_xml(xml_file):
    """
    Extract image dimensions from LabelMe 3.0 XML file.
    
    Args:
        xml_file (str): Path to the XML file
        
    Returns:
        tuple: (width, height) or None if not found
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find image size
        size_elem = root.find(".//size")
        if size_elem is not None:
            width = int(size_elem.find("width").text)
            height = int(size_elem.find("height").text)
            return width, height
        return None
    except Exception as e:
        print(f"Error getting image size from {xml_file}: {str(e)}")
        return None


def labelme3_to_via(input_dir, output_dir="dst"):
    """
    Convert LabelMe 3.0 (XML) format annotations to VIA (JSON) format.
    
    Args:
        input_dir (str): Directory containing LabelMe 3.0 XML files
        output_dir (str, optional): Output directory for VIA JSON. Defaults to "dst".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory
        if not clean_dir(output_dir):
            print(f"Failed to create output directory {output_dir}")
            return False
            
        print(f"Converting LabelMe 3.0 annotations from {input_dir} to VIA format...")
        
        # Find all XML files
        xml_files = [f for f in os.listdir(input_dir) if f.endswith('.xml')]
        
        if not xml_files:
            print(f"No LabelMe 3.0 XML files found in {input_dir}")
            return False
            
        print(f"Processing {len(xml_files)} LabelMe 3.0 XML files...")
        
        # Initialize VIA JSON structure
        via_json = {
            "_via_settings": {
                "ui": {
                    "annotation_editor_height": 25,
                    "annotation_editor_fontsize": 0.8,
                    "leftsidebar_width": 18,
                    "image_grid": {
                        "img_height": 80,
                        "rshape_fill": "none",
                        "rshape_fill_opacity": 0.3,
                        "rshape_stroke": "yellow",
                        "rshape_stroke_width": 2,
                        "show_region_shape": True,
                        "show_image_policy": "all"
                    }
                },
                "core": {
                    "buffer_size": 18,
                    "filepath": {},
                    "default_filepath": ""
                },
                "project": {
                    "name": "LabelMe3 to VIA conversion"
                }
            },
            "_via_img_metadata": {},
            "_via_attributes": {
                "region": {
                    "type": {
                        "type": "dropdown",
                        "description": "Region type",
                        "options": {
                            "rect": "Rectangle",
                            "polygon": "Polygon"
                        },
                        "default_options": {
                            "rect": True
                        }
                    },
                    "name": {
                        "type": "text",
                        "description": "Object name",
                        "default_value": ""
                    }
                },
                "file": {}
            }
        }
        
        converted_count = 0
        for xml_file in xml_files:
            try:
                # Parse XML file
                xml_path = os.path.join(input_dir, xml_file)
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Get filename
                filename_elem = root.find("filename")
                if filename_elem is None:
                    print(f"Warning: No filename found in {xml_file}. Using XML filename.")
                    image_filename = os.path.splitext(xml_file)[0]
                else:
                    image_filename = filename_elem.text
                
                # Get image dimensions
                img_size = get_image_size_from_xml(xml_path)
                if img_size is None:
                    print(f"Warning: Could not determine image size for {xml_file}. Skipping.")
                    continue
                    
                width, height = img_size
                
                # Find corresponding image file
                image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
                image_path = None
                
                for ext in image_extensions:
                    img_file = f"{os.path.splitext(image_filename)[0]}{ext}"
                    img_path = os.path.join(input_dir, img_file)
                    if os.path.exists(img_path):
                        image_path = img_path
                        break
                
                if not image_path:
                    print(f"Warning: No image found for {xml_file}. Skipping.")
                    continue
                
                # Copy image to destination
                dest_img_path = os.path.join(output_dir, os.path.basename(image_path))
                Path(image_path).copy(dest_img_path)
                
                # Create VIA image metadata
                image_id = os.path.basename(image_path) + str(os.path.getsize(image_path))
                via_json["_via_img_metadata"][image_id] = {
                    "filename": os.path.basename(image_path),
                    "size": os.path.getsize(image_path),
                    "regions": [],
                    "file_attributes": {}
                }
                
                # Process objects (regions)
                region_id = 0
                for obj in root.findall(".//object"):
                    name_elem = obj.find("name")
                    if name_elem is None:
                        continue
                        
                    name = name_elem.text
                    
                    # Process bounding box
                    bndbox = obj.find("bndbox")
                    if bndbox is not None:
                        # Rectangle annotation
                        xmin = int(float(bndbox.find("xmin").text))
                        ymin = int(float(bndbox.find("ymin").text))
                        xmax = int(float(bndbox.find("xmax").text))
                        ymax = int(float(bndbox.find("ymax").text))
                        
                        region = {
                            "shape_attributes": {
                                "name": "rect",
                                "x": xmin,
                                "y": ymin,
                                "width": xmax - xmin,
                                "height": ymax - ymin
                            },
                            "region_attributes": {
                                "name": name,
                                "type": "rect"
                            }
                        }
                        
                        via_json["_via_img_metadata"][image_id]["regions"].append(region)
                        region_id += 1
                        
                converted_count += 1
                
            except Exception as e:
                print(f"Error processing {xml_file}: {str(e)}")
        
        # Write VIA JSON to file
        output_json_path = os.path.join(output_dir, "via_project.json")
        with open(output_json_path, 'w') as f:
            json.dump(via_json, f, indent=2)
            
        print(f"Conversion complete. {converted_count} annotations converted to VIA format.")
        print(f"Results saved to {output_dir}")
        print(f"VIA project file saved as {output_json_path}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert LabelMe 3.0 format annotations to VIA format")
    parser.add_argument('--input_dir', required=True, help="Directory containing LabelMe 3.0 XML files")
    parser.add_argument('--output_dir', default="dst", help="Output directory for VIA JSON")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    labelme3_to_via(args.input_dir, args.output_dir)