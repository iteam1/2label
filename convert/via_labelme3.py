"""
Convert VIA (VGG Image Annotator) format to LabelMe 3.0 format.

Usage:
    python via_labelme3.py --input_dir /path/to/via --output_dir /path/to/output
"""

import os
import sys
import json
import argparse
import shutil
from xml.dom import minidom
from PIL import Image
from pathlib import Path

from .utils import ensure_dir, clean_dir


def create_xml_document(img_name, img_width, img_height, regions):
    """
    Create a LabelMe 3.0 XML document from VIA annotations.
    
    Args:
        img_name (str): Image filename
        img_width (int): Image width
        img_height (int): Image height
        regions (list): List of VIA region annotations
        
    Returns:
        xml.dom.minidom.Document: XML document in LabelMe 3.0 format
    """
    # Create XML document
    root = minidom.Document()
    
    # Create annotation tag
    xml = root.createElement('annotation')
    root.appendChild(xml)
    
    # Create filename tag
    filename = root.createElement('filename')
    filename.appendChild(root.createTextNode(img_name))
    xml.appendChild(filename)
    
    # Create folder tag
    folder = root.createElement('folder')
    folder.appendChild(root.createTextNode('images'))
    xml.appendChild(folder)
    
    # Create source tag
    source = root.createElement('source')
    xml.appendChild(source)
    
    # Add source database
    database = root.createElement('database')
    database.appendChild(root.createTextNode('VIA to LabelMe 3.0 Converter'))
    source.appendChild(database)
    
    # Add source annotation
    annotation_tag = root.createElement('annotation')
    annotation_tag.appendChild(root.createTextNode('VIA'))
    source.appendChild(annotation_tag)
    
    # Add source image
    image_tag = root.createElement('image')
    image_tag.appendChild(root.createTextNode('Unknown'))
    source.appendChild(image_tag)
    
    # Create size tag
    size = root.createElement('size')
    xml.appendChild(size)
    
    # Add width
    width = root.createElement('width')
    width.appendChild(root.createTextNode(str(img_width)))
    size.appendChild(width)
    
    # Add height
    height = root.createElement('height')
    height.appendChild(root.createTextNode(str(img_height)))
    size.appendChild(height)
    
    # Add depth (assuming RGB)
    depth = root.createElement('depth')
    depth.appendChild(root.createTextNode('3'))
    size.appendChild(depth)
    
    # Create segmented tag
    segmented = root.createElement('segmented')
    segmented.appendChild(root.createTextNode('0'))
    xml.appendChild(segmented)
    
    # Process regions
    for region in regions:
        # Get region attributes
        shape_attrs = region.get('shape_attributes', {})
        region_attrs = region.get('region_attributes', {})
        
        shape_type = shape_attrs.get('name')
        
        # Only process supported shapes
        if shape_type not in ['rect', 'polygon']:
            continue
            
        # Create object tag
        obj = root.createElement('object')
        xml.appendChild(obj)
        
        # Add name (label)
        name = root.createElement('name')
        label = region_attrs.get('label', region_attrs.get('labels', 'unknown'))
        name.appendChild(root.createTextNode(str(label)))
        obj.appendChild(name)
        
        # Add pose
        pose = root.createElement('pose')
        pose.appendChild(root.createTextNode('Unspecified'))
        obj.appendChild(pose)
        
        # Add truncated
        truncated = root.createElement('truncated')
        truncated.appendChild(root.createTextNode('0'))
        obj.appendChild(truncated)
        
        # Add difficult
        difficult = root.createElement('difficult')
        difficult.appendChild(root.createTextNode('0'))
        obj.appendChild(difficult)
        
        # Add bndbox or polygon
        if shape_type == 'rect':
            # For rectangle annotations
            bndbox = root.createElement('bndbox')
            obj.appendChild(bndbox)
            
            # Get coordinates
            x = shape_attrs.get('x', 0)
            y = shape_attrs.get('y', 0)
            width = shape_attrs.get('width', 0)
            height = shape_attrs.get('height', 0)
            
            # Add bounding box coordinates
            xmin = root.createElement('xmin')
            xmin.appendChild(root.createTextNode(str(x)))
            bndbox.appendChild(xmin)
            
            ymin = root.createElement('ymin')
            ymin.appendChild(root.createTextNode(str(y)))
            bndbox.appendChild(ymin)
            
            xmax = root.createElement('xmax')
            xmax.appendChild(root.createTextNode(str(x + width)))
            bndbox.appendChild(xmax)
            
            ymax = root.createElement('ymax')
            ymax.appendChild(root.createTextNode(str(y + height)))
            bndbox.appendChild(ymax)
            
        elif shape_type == 'polygon':
            # For polygon annotations
            polygon = root.createElement('polygon')
            obj.appendChild(polygon)
            
            # Get points
            all_points_x = shape_attrs.get('all_points_x', [])
            all_points_y = shape_attrs.get('all_points_y', [])
            
            # Add points
            for i in range(len(all_points_x)):
                pt = root.createElement('pt')
                polygon.appendChild(pt)
                
                x_coord = root.createElement('x')
                x_coord.appendChild(root.createTextNode(str(all_points_x[i])))
                pt.appendChild(x_coord)
                
                y_coord = root.createElement('y')
                y_coord.appendChild(root.createTextNode(str(all_points_y[i])))
                pt.appendChild(y_coord)
    
    return root


def via_to_labelme3(input_dir, output_dir="dst"):
    """
    Convert VIA JSON format to LabelMe 3.0 XML format.
    
    Args:
        input_dir (str): Directory containing VIA JSON file and images
        output_dir (str, optional): Output directory for LabelMe 3.0 files. Defaults to "dst".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory
        if not clean_dir(output_dir):
            print(f"Failed to create output directory {output_dir}")
            return False
            
        # Supported annotation types
        annotation_types = ['rect', 'polygon']
        
        # Find VIA JSON file
        via_json_path = os.path.join(input_dir, 'via_region_data.json')
        if not os.path.exists(via_json_path):
            print(f"VIA JSON file not found at {via_json_path}")
            return False
            
        # Load VIA JSON data
        try:
            with open(via_json_path, 'r') as f:
                via_data = json.load(f)
        except Exception as e:
            print(f"Failed to load VIA JSON file: {str(e)}")
            return False
            
        if not via_data:
            print("VIA JSON file is empty or invalid")
            return False
            
        print(f"Processing {len(via_data)} images from VIA project")
        
        # Process each image in VIA data
        for i, (image_key, image_data) in enumerate(via_data.items()):
            try:
                # Get image filename
                img_name = image_data.get('filename')
                if not img_name:
                    print(f"Warning: Image at index {i} has no filename. Skipping.")
                    continue
                    
                print(f"Processing image {i+1}/{len(via_data)}: {img_name}")
                
                # Get image dimensions
                img_path = os.path.join(input_dir, img_name)
                if not os.path.exists(img_path):
                    print(f"Warning: Image file {img_path} not found. Skipping.")
                    continue
                    
                try:
                    with Image.open(img_path) as img:
                        img_width, img_height = img.size
                except Exception as e:
                    print(f"Warning: Failed to open image {img_path}: {str(e)}. Skipping.")
                    continue
                    
                # Get regions
                regions = image_data.get('regions', [])
                if not regions:
                    print(f"Warning: No annotations found for {img_name}. Skipping.")
                    continue
                    
                # Create XML document
                xml_doc = create_xml_document(img_name, img_width, img_height, regions)
                
                # Save XML file
                xml_filename = os.path.splitext(img_name)[0] + '.xml'
                xml_path = os.path.join(output_dir, xml_filename)
                
                with open(xml_path, 'w') as f:
                    f.write(xml_doc.toprettyxml())
                    
                # Copy image file
                dst_img_path = os.path.join(output_dir, img_name)
                try:
                    Path(img_path).copy(dst_img_path)
                except Exception as e:
                    print(f"Warning: Failed to copy image {img_path}: {str(e)}")
                    
            except Exception as e:
                print(f"Error processing image {image_key}: {str(e)}")
        
        print(f"Conversion complete. Results saved to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert VIA JSON to LabelMe 3.0 XML format")
    parser.add_argument('--input_dir', required=True, help="Directory containing VIA JSON file and images")
    parser.add_argument('--output_dir', default="dst", help="Output directory for LabelMe 3.0 files")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    via_to_labelme3(args.input_dir, args.output_dir)