# CVAT to YOLO Conversion Guide

This guide explains how to convert CVAT XML format annotations to YOLO format using the 2Label conversion tool.

## CVAT Format

CVAT (Computer Vision Annotation Tool) uses an XML-based format for annotations. The annotations are typically stored in a single XML file that contains information about:

- Tasks and jobs
- Image metadata (name, size)
- Labels/classes
- Annotations for each image (bounding boxes, polygons, etc.)

Example of a CVAT XML file structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<annotations>
  <version>1.1</version>
  <meta>
    <task>
      <id>1</id>
      <name>task_name</name>
      <labels>
        <label>
          <name>car</name>
          <attributes>
          </attributes>
        </label>
        <label>
          <name>person</name>
          <attributes>
          </attributes>
        </label>
      </labels>
    </task>
  </meta>
  <image id="0" name="image1.jpg" width="800" height="600">
    <box label="car" xtl="100" ytl="50" xbr="300" ybr="200" />
    <box label="person" xtl="400" ytl="150" xbr="450" ybr="300" />
  </image>
  <image id="1" name="image2.jpg" width="800" height="600">
    <box label="car" xtl="200" ytl="100" xbr="400" ybr="250" />
  </image>
</annotations>
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

The CVAT to YOLO converter in 2Label:

1. Extracts all class names from the CVAT XML file
2. Creates a `classes.txt` file with the extracted class names
3. For each image in the CVAT XML:
   - Extracts bounding box annotations
   - Converts coordinates from CVAT format (absolute top-left and bottom-right) to YOLO format (normalized center, width, height)
   - Creates a corresponding YOLO text file
4. Copies the image files to the output directory

## Usage

### Command Line

```bash
python -m convert cvat-to-yolo --input_dir /path/to/cvat_dataset --output_dir /path/to/output
```

### Python API

```python
from convert import cvat_to_yolo

# Convert CVAT to YOLO
cvat_to_yolo(input_dir="/path/to/cvat_dataset", output_dir="/path/to/output")
```

## Tips for Successful Conversion

1. Ensure the CVAT XML file is in the same directory as the image files
2. Make sure the image names in the CVAT XML match the actual image files
3. Verify that all bounding box coordinates are valid
4. Check the generated `classes.txt` file to ensure all classes are correctly extracted

## Limitations

- Only bounding box annotations are supported (polygons, polylines, and other shapes are ignored)
- Only the first CVAT XML file found in the input directory is processed
- Attributes associated with annotations in CVAT are not preserved in YOLO format

## Common Issues

- **Missing image files**: The converter will skip images mentioned in the CVAT XML but not found in the input directory
- **Invalid coordinates**: Bounding boxes with invalid coordinates will be skipped
- **Duplicate class names**: Class names must be unique in the CVAT XML file
