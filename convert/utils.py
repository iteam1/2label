"""
Utility functions for annotation format conversions.
"""

import os
import json
import shutil
import base64
from PIL import Image


def ensure_dir(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False


def clean_dir(directory):
    """
    Clean a directory if it exists, or create it if it doesn't.
    
    Args:
        directory: Path to the directory to clean/create
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        Exception: If the directory exists and cannot be cleaned
    """
    if os.path.exists(directory):
        try:
            shutil.rmtree(directory)
            os.makedirs(directory)
            return True
        except Exception as e:
            raise Exception(f"Failed to clean directory {directory}: {str(e)}")
    else:
        os.makedirs(directory)
        return True


def get_image_dimensions(image_path):
    """
    Get the dimensions of an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        tuple: (width, height) of the image
    """
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        raise Exception(f"Failed to get image dimensions for {image_path}: {str(e)}")


def image_to_base64(image_path):
    """
    Convert an image to base64 encoding.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Base64 encoded image string
    """
    try:
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            return img_base64
    except Exception as e:
        raise Exception(f"Failed to convert image to base64 for {image_path}: {str(e)}")


def save_json(data, json_path):
    """
    Save data as JSON file.
    
    Args:
        data: Data to save as JSON
        json_path: Path to save the JSON file
        
    Returns:
        bool: True if successful
    """
    try:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        raise Exception(f"Failed to save JSON to {json_path}: {str(e)}")


def load_json(json_path):
    """
    Load JSON data from a file.
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        dict: Loaded JSON data
    """
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load JSON from {json_path}: {str(e)}")
