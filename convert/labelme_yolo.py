"""
Convert LabelMe format annotations to YOLO format.

Usage:
    python labelme_yolo.py --input_dir /path/to/labelme --output_dir /path/to/output
"""

import os
import sys
import json
import argparse
from pathlib import Path
import shutil
from collections import defaultdict

from .utils import ensure_dir, clean_dir, load_json_file


def parse_labelme_json(json_file, class_mapping=None):
    """
    Parse LabelMe JSON annotation file.
    
    Args:
        json_file (str): Path to LabelMe JSON file
        class_mapping (dict, optional): Mapping of class names to class IDs. If None, a new mapping will be created.
        
    Returns:
        tuple: (shapes, image_width, image_height, updated_class_mapping)
    """
    try:
        # Load JSON file
        data = load_json_file(json_file)
        if not data:
            return None, None, None, class_mapping
            
        # Get image dimensions
        image_width = data.get("imageWidth")
        image_height = data.get("imageHeight")
        
        # If dimensions aren't in the JSON, we can't proceed
        if not image_width or not image_height:
            print(f"Warning: No image dimensions found in {json_file}")
            return None, None, None, class_mapping
            
        # Initialize class mapping if not provided
        if class_mapping is None:
            class_mapping = {}
            
        # Process shapes (annotations)
        shapes = []
        for shape in data.get("shapes", []):
            label = shape.get("label")
            shape_type = shape.get("shape_type")
            points = shape.get("points")
            
            # Skip if missing required data
            if not label or not shape_type or not points:
                continue
                
            # Only process rectangles (bounding boxes)
            if shape_type != "rectangle":
                print(f"Warning: Shape type '{shape_type}' in {json_file} is not supported. Only 'rectangle' is supported.")
                continue
                
            # Add label to class mapping if not already present
            if label not in class_mapping:
                class_mapping[label] = len(class_mapping)
                
            # Get class ID
            class_id = class_mapping[label]
            
            # Extract bounding box coordinates
            if len(points) == 2:  # LabelMe rectangles have 2 points: top-left and bottom-right
                x1, y1 = points[0]
                x2, y2 = points[1]
                
                # Ensure coordinates are valid
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                # Convert to YOLO format (normalized center, width, height)
                x_center = (x1 + x2) / (2 * image_width)
                y_center = (y1 + y2) / (2 * image_height)
                box_width = (x2 - x1) / image_width
                box_height = (y2 - y1) / image_height
                
                # Validate coordinates
                if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 
                        0 <= box_width <= 1 and 0 <= box_height <= 1):
                    print(f"Warning: Invalid box coordinates in {json_file}, label {label}")
                    continue
                    
                shapes.append({
                    "class_id": class_id,
                    "x_center": x_center,
                    "y_center": y_center,
                    "width": box_width,
                    "height": box_height
                })
                
        return shapes, image_width, image_height, class_mapping
        
    except Exception as e:
        print(f"Error parsing LabelMe JSON file {json_file}: {str(e)}")
        return None, None, None, class_mapping


def write_yolo_files(annotations, class_mapping, input_dir, output_dir):
    """
    Write YOLO annotation files and copy images.
    
    Args:
        annotations (dict): Dictionary mapping image filenames to annotations
        class_mapping (dict): Mapping of class names to class IDs
        input_dir (str): Input directory containing LabelMe files
        output_dir (str): Output directory for YOLO format
        
    Returns:
        int: Number of processed files
    """
    try:
        # Write classes.txt
        classes = [""] * len(class_mapping)
        for label, class_id in class_mapping.items():
            classes[class_id] = label
            
        with open(os.path.join(output_dir, 'classes.txt'), 'w') as f:
            f.write('\n'.join(classes))
            
        # Process each annotation
        processed_count = 0
        for image_filename, annotation_data in annotations.items():
            # Get annotations
            shapes = annotation_data.get("shapes", [])
            if not shapes:
                continue
                
            # Find image file
            image_path = os.path.join(input_dir, image_filename)
            if not os.path.exists(image_path):
                print(f"Warning: Image {image_filename} not found in {input_dir}")
                continue
                
            # Copy image to output directory
            output_image_path = os.path.join(output_dir, image_filename)
            try:
                shutil.copy2(image_path, output_image_path)
            except Exception as e:
                print(f"Error copying image {image_path}: {str(e)}")
                continue
                
            # Write YOLO annotation
            base_name = os.path.splitext(image_filename)[0]
            txt_path = os.path.join(output_dir, f"{base_name}.txt")
            
            with open(txt_path, 'w') as f:
                for shape in shapes:
                    # YOLO format: class_id center_x center_y width height
                    f.write(f"{shape['class_id']} {shape['x_center']:.6f} "
                           f"{shape['y_center']:.6f} {shape['width']:.6f} "
                           f"{shape['height']:.6f}\n")
                    
            processed_count += 1
            
        return processed_count
        
    except Exception as e:
        print(f"Error writing YOLO files: {str(e)}")
        return 0


def labelme_to_yolo(input_dir, output_dir="dst"):
    """
    Convert LabelMe format annotations to YOLO format.
    
    Args:
        input_dir (str): Directory containing LabelMe JSON files
        output_dir (str, optional): Output directory for YOLO files. Defaults to "dst".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory
        if not clean_dir(output_dir):
            print(f"Failed to create output directory {output_dir}")
            return False
            
        print(f"Converting LabelMe annotations from {input_dir} to YOLO format...")
        
        # Find all JSON files
        json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
        
        if not json_files:
            print(f"No LabelMe JSON files found in {input_dir}")
            return False
            
        print(f"Found {len(json_files)} LabelMe JSON files")
        
        # Process all JSON files
        class_mapping = {}
        annotations = {}
        
        for json_file in json_files:
            json_path = os.path.join(input_dir, json_file)
            
            # Get image filename from JSON
            image_filename = None
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    image_filename = data.get("imagePath")
            except Exception as e:
                print(f"Error reading {json_path}: {str(e)}")
                continue
                
            if not image_filename:
                print(f"Warning: No image path found in {json_file}")
                continue
                
            # Handle relative paths
            image_filename = os.path.basename(image_filename)
            
            # Parse LabelMe JSON
            shapes, width, height, class_mapping = parse_labelme_json(json_path, class_mapping)
            
            if shapes:
                annotations[image_filename] = {
                    "shapes": shapes,
                    "width": width,
                    "height": height
                }
                
        if not annotations:
            print("No valid annotations found")
            return False
            
        # Print class information
        print(f"Found {len(class_mapping)} classes:")
        for label, class_id in sorted(class_mapping.items(), key=lambda x: x[1]):
            print(f"  {class_id}: {label}")
            
        # Write YOLO files
        processed_count = write_yolo_files(annotations, class_mapping, input_dir, output_dir)
        
        print(f"Conversion complete. {processed_count}/{len(annotations)} images converted to YOLO format.")
        print(f"Results saved to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert LabelMe format annotations to YOLO format")
    parser.add_argument('--input_dir', required=True, help="Directory containing LabelMe JSON files")
    parser.add_argument('--output_dir', default="dst", help="Output directory for YOLO files")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    labelme_to_yolo(args.input_dir, args.output_dir)
