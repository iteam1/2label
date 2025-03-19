# LabelMe to YOLO Conversion Guide

This guide explains how to convert LabelMe format annotations to YOLO format using the 2Label conversion tool.

## LabelMe Format

LabelMe uses a JSON format for annotations where each image has a corresponding JSON file. The JSON file contains:

- Image information (filename, dimensions)
- Shapes (annotations) with label and points
- Flags and other metadata

Example of a LabelMe JSON file:

```json
{
  "version": "4.5.6",
  "flags": {},
  "shapes": [
    {
      "label": "car",
      "points": [
        [100, 50],
        [300, 200]
      ],
      "group_id": null,
      "shape_type": "rectangle",
      "flags": {}
    },
    {
      "label": "person",
      "points": [
        [400, 150],
        [450, 300]
      ],
      "group_id": null,
      "shape_type": "rectangle",
      "flags": {}
    }
  ],
  "imagePath": "image1.jpg",
  "imageData": "...",
  "imageHeight": 600,
  "imageWidth": 800
}
```

## YOLO Format

YOLO (You Only Look Once) uses a simple text-based format for annotations. For each image, there is a corresponding text file with the same name but with a `.txt` extension. Each line in the text file represents one object:

```
<class_id> <x_center> <y_center> <width> <height>
```

Where:
- `class_id`: Integer class ID (0-based)
- `x_center`, `y_center`: Normalized coordinates (0-1) of the center of the bounding box
- `width`, `height`: Normalized width and height of the bounding box

Example of a YOLO text file:
```
0 0.5 0.5 0.25 0.25
1 0.7 0.8 0.15 0.3
```

YOLO format also typically includes a `classes.txt` file listing all class names, one per line.

## Conversion Process

The LabelMe to YOLO converter in 2Label:

1. Scans the input directory for LabelMe JSON files
2. Creates a mapping of class names to class IDs
3. Extracts bounding box annotations from each JSON file
4. Converts coordinates from LabelMe format (absolute top-left and bottom-right points) to YOLO format (normalized center, width, height)
5. Writes a YOLO text file for each image
6. Creates a `classes.txt` file with all unique class names

## Usage

### Command Line

```bash
python -m convert labelme-to-yolo --input_dir /path/to/labelme_dataset --output_dir /path/to/output
```

### Python API

```python
from convert import labelme_to_yolo

# Convert LabelMe to YOLO
labelme_to_yolo(input_dir="/path/to/labelme_dataset", output_dir="/path/to/output")
```

## Tips for Successful Conversion

1. Ensure all LabelMe JSON files have the correct `imagePath` that points to an existing image file
2. Only rectangle shapes are supported for conversion to YOLO format
3. Make sure the `imageWidth` and `imageHeight` fields are correctly set in each JSON file
4. Check that bounding box coordinates are valid (within image boundaries)

## Limitations

- Only rectangle (bounding box) annotations are supported (polygons, lines, and other shapes are ignored)
- LabelMe files must have valid image dimensions specified
- The LabelMe files must be in JSON format (not the older XML format used by LabelMe 3.0)

## Common Issues

- **Missing image files**: The converter will skip JSON files that reference missing images
- **Invalid coordinates**: Bounding boxes with invalid coordinates will be skipped
- **Unsupported shape types**: Non-rectangle shapes will be skipped with a warning
- **Missing image dimensions**: JSON files without valid image dimensions will be skipped
