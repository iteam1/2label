"""
Convert LabelMe JSON format to COCO format.

Usage:
    python labelme_coco.py --input_dir /path/to/labelme --output_file /path/to/coco.json
"""

import os
import argparse
import json
import glob
from datetime import datetime

import numpy as np
from PIL import Image
from labelme import utils


class LabelMeToCOCO:
    """Class to convert LabelMe JSON format to COCO format."""
    
    def __init__(self, labelme_files=None, output_file="coco.json"):
        """
        Initialize the converter.
        
        Args:
            labelme_files (list): List of LabelMe JSON file paths
            output_file (str): Path to save the output COCO JSON file
        """
        self.labelme_files = labelme_files or []
        self.output_file = output_file
        self.images = []
        self.categories = []
        self.annotations = []
        self.labels = []
        self.annotation_id = 1
        self.height = 0
        self.width = 0
        
    def process_data(self):
        """Process LabelMe data and convert to COCO format."""
        for file_index, json_file in enumerate(self.labelme_files):
            try:
                data = self._load_json_file(json_file)
                if not data:
                    continue
                    
                # Process image info
                image_id = file_index
                self._process_image(data, image_id, json_file)
                
                # Process shapes (annotations)
                self._process_shapes(data, image_id)
                
            except Exception as e:
                print(f"Error processing file {json_file}: {str(e)}")
        
        # Update category IDs in the annotations
        self._update_category_ids()
        
    def _load_json_file(self, json_file):
        """Load a LabelMe JSON file."""
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading {json_file}: {str(e)}")
            return None
            
    def _process_image(self, data, image_id, json_file):
        """Process image data and add to images list."""
        try:
            # Get image dimensions
            if "imageWidth" in data and "imageHeight" in data:
                self.height = data["imageHeight"]
                self.width = data["imageWidth"]
            else:
                # Try to get image size from file
                img_file = data.get("imagePath")
                if img_file:
                    img_path = os.path.join(os.path.dirname(json_file), img_file)
                    if os.path.exists(img_path):
                        with Image.open(img_path) as img:
                            self.width, self.height = img.size
                    else:
                        print(f"Warning: Image file {img_path} not found")
                
            # Create image info
            image = {
                "height": self.height,
                "width": self.width,
                "id": image_id,
                "file_name": os.path.basename(data.get("imagePath", f"image_{image_id}.jpg"))
            }
            self.images.append(image)
            
        except Exception as e:
            print(f"Error processing image data for {json_file}: {str(e)}")
            
    def _process_shapes(self, data, image_id):
        """Process shape data and add to annotations list."""
        for shape in data.get("shapes", []):
            try:
                label = shape.get("label")
                if label not in self.labels:
                    self.labels.append(label)
                    
                # Get annotation data
                points = shape.get("points", [])
                shape_type = shape.get("shape_type", "polygon")
                
                if shape_type == "polygon":
                    # Convert points to numpy array
                    points_array = np.array(points)
                    x = points_array[:, 0]
                    y = points_array[:, 1]
                    
                    # Create segmentation
                    segmentation = [points_array.flatten().tolist()]
                    
                    # Create bounding box
                    x_min = np.min(x)
                    y_min = np.min(y)
                    x_max = np.max(x)
                    y_max = np.max(y)
                    width = x_max - x_min
                    height = y_max - y_min
                    bbox = [x_min, y_min, width, height]
                    
                    # Create area
                    area = self._calculate_area(points_array)
                    
                    # Create annotation
                    annotation = {
                        "segmentation": segmentation,
                        "area": area,
                        "iscrowd": 0,
                        "image_id": image_id,
                        "bbox": bbox,
                        "category_id": -1,  # Will be updated later
                        "id": self.annotation_id,
                        "category_name": label  # Temporary field
                    }
                    
                    self.annotations.append(annotation)
                    self.annotation_id += 1
                    
                elif shape_type == "rectangle":
                    # For rectangle, we have two points: top-left and bottom-right
                    if len(points) == 2:
                        x1, y1 = points[0]
                        x2, y2 = points[1]
                        
                        # Create bounding box
                        x_min = min(x1, x2)
                        y_min = min(y1, y2)
                        width = abs(x2 - x1)
                        height = abs(y2 - y1)
                        bbox = [x_min, y_min, width, height]
                        
                        # Create segmentation (rectangle to polygon)
                        segmentation = [[x_min, y_min, x_min + width, y_min,
                                        x_min + width, y_min + height, x_min, y_min + height]]
                        
                        # Create area
                        area = width * height
                        
                        # Create annotation
                        annotation = {
                            "segmentation": segmentation,
                            "area": area,
                            "iscrowd": 0,
                            "image_id": image_id,
                            "bbox": bbox,
                            "category_id": -1,  # Will be updated later
                            "id": self.annotation_id,
                            "category_name": label  # Temporary field
                        }
                        
                        self.annotations.append(annotation)
                        self.annotation_id += 1
                
            except Exception as e:
                print(f"Error processing shape {shape}: {str(e)}")
                
    def _calculate_area(self, points_array):
        """Calculate the area of a polygon."""
        return 0.5 * abs(np.dot(points_array[:, 0], np.roll(points_array[:, 1], 1)) - 
                        np.dot(points_array[:, 1], np.roll(points_array[:, 0], 1)))
                
    def _update_category_ids(self):
        """Update category IDs in annotations and create categories list."""
        for i, label in enumerate(self.labels):
            category = {
                "supercategory": "object",
                "id": i + 1,
                "name": label
            }
            self.categories.append(category)
            
        # Update category IDs in annotations
        for annotation in self.annotations:
            category_name = annotation.pop("category_name", None)
            if category_name:
                category_id = self.labels.index(category_name) + 1
                annotation["category_id"] = category_id
                
    def save(self):
        """Save the COCO format data to a JSON file."""
        try:
            data = {
                "info": {
                    "description": "Converted from LabelMe format",
                    "url": "",
                    "version": "1.0",
                    "year": datetime.now().year,
                    "contributor": "LabelMe to COCO Converter",
                    "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "licenses": [{
                    "id": 1,
                    "name": "Unknown",
                    "url": ""
                }],
                "images": self.images,
                "annotations": self.annotations,
                "categories": self.categories
            }
            
            with open(self.output_file, "w") as f:
                json.dump(data, f, indent=2)
                
            print(f"Conversion complete. Output saved to {self.output_file}")
            print(f"  - Images: {len(self.images)}")
            print(f"  - Categories: {len(self.categories)}")
            print(f"  - Annotations: {len(self.annotations)}")
            
            return True
            
        except Exception as e:
            print(f"Error saving COCO data: {str(e)}")
            return False


def labelme_to_coco(input_dir, output_file="coco.json"):
    """
    Convert LabelMe JSON files to COCO format.
    
    Args:
        input_dir (str): Directory containing LabelMe JSON files
        output_file (str, optional): Output COCO JSON file. Defaults to "coco.json".
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Find all JSON files
        labelme_files = glob.glob(os.path.join(input_dir, "*.json"))
        
        if not labelme_files:
            print(f"No JSON files found in {input_dir}")
            return False
            
        print(f"Converting {len(labelme_files)} LabelMe JSON files to COCO format...")
        
        # Convert to COCO format
        converter = LabelMeToCOCO(labelme_files, output_file)
        converter.process_data()
        return converter.save()
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert LabelMe JSON files to COCO format")
    parser.add_argument("--input_dir", required=True, help="Directory containing LabelMe JSON files")
    parser.add_argument("--output_file", default="coco.json", help="Output COCO JSON file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    labelme_to_coco(args.input_dir, args.output_file)
