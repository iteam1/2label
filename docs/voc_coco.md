# VOC to COCO Conversion Guide

This guide explains how to convert Pascal VOC format annotations to COCO format using the 2Label conversion tool.

## Pascal VOC Format

Pascal VOC (Visual Object Classes) is an XML-based annotation format widely used for object detection. Each image has a corresponding XML file with the same name (but with an .xml extension) that contains:

- Image information (filename, size)
- Object annotations (class name, bounding box coordinates)

Example of a Pascal VOC XML file:

```xml
<annotation>
    <folder>VOC2007</folder>
    <filename>000001.jpg</filename>
    <size>
        <width>500</width>
        <height>375</height>
        <depth>3</depth>
    </size>
    <object>
        <name>car</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>156</xmin>
            <ymin>97</ymin>
            <xmax>351</xmax>
            <ymax>270</ymax>
        </bndbox>
    </object>
</annotation>
```

## COCO Format

COCO (Common Objects in Context) uses a single JSON file for the entire dataset. The JSON file contains arrays for:

- Images (with id, filename, size)
- Categories (object classes)
- Annotations (bounding boxes, segmentations, etc.)

Example of a COCO JSON structure:

```json
{
  "info": { ... },
  "licenses": [ ... ],
  "images": [
    {
      "id": 1,
      "width": 500,
      "height": 375,
      "file_name": "000001.jpg"
    },
    ...
  ],
  "categories": [
    {
      "id": 1,
      "name": "car",
      "supercategory": "object"
    },
    ...
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [156, 97, 195, 173],
      "area": 33735,
      "iscrowd": 0
    },
    ...
  ]
}
```

## Conversion Process

The VOC to COCO converter in 2Label:

1. Scans all XML files in the input directory
2. Extracts image information and object annotations
3. Creates a COCO JSON structure
4. Automatically generates a category list from class names
5. Converts VOC bounding box format (xmin, ymin, xmax, ymax) to COCO format (x, y, width, height)

## Usage

### Command Line

```bash
python -m convert voc-to-coco --input_dir /path/to/voc_dataset --output_file /path/to/output.json
```

### Python API

```python
from convert import voc_to_coco

# Convert VOC to COCO
voc_to_coco(input_dir="/path/to/voc_dataset", output_file="/path/to/output.json")
```

## Tips for Successful Conversion

1. Ensure all XML files have corresponding image files in the same directory
2. Make sure all XML files are valid and properly formatted
3. Check that all objects have proper bounding box coordinates
4. The resulting COCO file can be validated using the [COCO API](https://github.com/cocodataset/cocoapi)

## Limitations

- Segmentation masks are not supported (empty arrays are created for COCO segmentation)
- Only bounding box annotations are transferred
- Additional VOC attributes like 'pose', 'truncated', and 'difficult' are not preserved in the COCO format

## Common Issues

- **Missing image files**: The converter will skip annotations with missing image files
- **Invalid XML**: Malformed XML files will be skipped with an error message
- **Duplicate categories**: Classes with the same name will be merged into a single category
