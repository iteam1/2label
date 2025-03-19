# 2Label Documentation

This directory contains documentation for different conversion workflows supported in 2Label.

## Available Conversion Guides

- [Pascal VOC to COCO Conversion](pascal_coco.md) - Guide for converting Pascal VOC format to COCO format
- [LabelImg to CVAT Conversion](labelImg_cvat.md) - Guide for converting LabelImg format to CVAT format
- [LabelMe to CVAT Conversion](labelme_cvat.md) - Guide for converting LabelMe format to CVAT format
- [VIA to CVAT Conversion](via_cvat.md) - Guide for converting VIA format to CVAT format
- [VOC to COCO Conversion](voc_coco.md) - Guide for converting VOC format to COCO format
- [CVAT to YOLO Conversion](cvat_yolo.md) - Guide for converting CVAT format to YOLO format
- [LabelMe to YOLO Conversion](labelme_yolo.md) - Guide for converting LabelMe format to YOLO format

## Conversion Matrix

| From / To | COCO | CVAT | LabelImg | LabelMe | VIA | YOLO | Pascal VOC |
|-----------|------|------|----------|---------|-----|------|------------|
| COCO      | -    | ✅   | ✅       | ✅      | ✅  | ✅   | ✅         |
| CVAT      | ✅   | -    | ✅       | ✅      | ✅  | ✅   | ❌         |
| LabelImg  | ✅   | ✅   | -        | ✅      | ✅  | ✅   | ✅         |
| LabelMe   | ✅   | ✅   | ✅       | -       | ✅  | ✅   | ✅         |
| VIA       | ✅   | ✅   | ✅       | ✅      | -   | ❌   | ❌         |
| YOLO      | ✅   | ✅   | ✅       | ✅      | ❌  | -    | ✅         |
| Pascal VOC| ✅   | ❌   | ✅       | ✅      | ❌  | ✅   | -          |

## Understanding Annotation Formats

### COCO Format
COCO (Common Objects in Context) uses a JSON structure with information about images, categories, and annotations. Learn more in the [COCO documentation](https://cocodataset.org/#format-data).

### CVAT Format
CVAT uses XML-based annotations. See the [CVAT documentation](https://github.com/opencv/cvat/blob/develop/cvat/apps/documentation/xml_format.md) for more details.

### LabelImg Format
LabelImg uses Pascal VOC format (XML files). Each image has a corresponding XML file.

### LabelMe Format
LabelMe uses JSON files for each image. Learn more in the [LabelMe documentation](https://github.com/wkentaro/labelme).

### VIA Format
VIA (VGG Image Annotator) uses a JSON format for annotations. Learn more in the [VIA documentation](https://www.robots.ox.ac.uk/~vgg/software/via/).

### YOLO Format
YOLO uses plain text files (.txt) with normalized coordinates. Each image has a corresponding text file.

### Pascal VOC Format
Pascal VOC uses XML files for annotations with information about objects, their bounding boxes, and classes.

## Adding New Documentation

If you're adding support for a new conversion workflow, please create a new markdown file with the following sections:

1. Overview
2. Prerequisites
3. Command syntax
4. Example usage
5. Notes and limitations

Please follow the existing documentation style.
