"""
2Label Conversion Package

This package provides tools for converting between different annotation formats.
"""

import argparse
import sys

from .labelme_coco import labelme_to_coco
from .labelme3_labelme import labelme3_to_labelme
from .via_labelme3 import via_to_labelme3
from .cvat_via import cvat_to_via
from .yolo_voc import yolo_to_voc
from .labelme3_via import labelme3_to_via
from .voc_coco import voc_to_coco
from .cvat_yolo import cvat_to_yolo
from .labelme_yolo import labelme_to_yolo

def main():
    """Main entry point for the 2label command-line interface."""
    parser = argparse.ArgumentParser(description="2Label: Convert between annotation formats")
    parser.add_argument('--version', action='version', version='2Label 0.1.0')
    
    subparsers = parser.add_subparsers(dest="command", help="Conversion commands")
    
    # LabelMe to COCO
    labelme_coco_parser = subparsers.add_parser("labelme-to-coco", help="Convert LabelMe to COCO")
    labelme_coco_parser.add_argument("--input_dir", required=True, help="Directory with LabelMe JSON files")
    labelme_coco_parser.add_argument("--output_file", required=True, help="Output COCO JSON file")
    
    # LabelMe to YOLO
    labelme_yolo_parser = subparsers.add_parser("labelme-to-yolo", help="Convert LabelMe to YOLO")
    labelme_yolo_parser.add_argument("--input_dir", required=True, help="Directory with LabelMe JSON files")
    labelme_yolo_parser.add_argument("--output_dir", default="dst", help="Output directory for YOLO files")
    
    # LabelMe3 to LabelMe
    labelme3_labelme_parser = subparsers.add_parser("labelme3-to-labelme", help="Convert LabelMe 3.0 to LabelMe")
    labelme3_labelme_parser.add_argument("--input_dir", required=True, help="Directory with LabelMe 3.0 files")
    labelme3_labelme_parser.add_argument("--output_dir", default="dst", help="Output directory for LabelMe files")
    
    # LabelMe3 to VIA
    labelme3_via_parser = subparsers.add_parser("labelme3-to-via", help="Convert LabelMe 3.0 to VIA")
    labelme3_via_parser.add_argument("--input_dir", required=True, help="Directory with LabelMe 3.0 files")
    labelme3_via_parser.add_argument("--output_dir", default="dst", help="Output directory for VIA files")
    
    # VIA to LabelMe3
    via_labelme3_parser = subparsers.add_parser("via-to-labelme3", help="Convert VIA to LabelMe 3.0")
    via_labelme3_parser.add_argument("--input_dir", required=True, help="Directory with VIA project file")
    via_labelme3_parser.add_argument("--output_dir", default="dst", help="Output directory for LabelMe 3.0 files")
    
    # CVAT to VIA
    cvat_via_parser = subparsers.add_parser("cvat-to-via", help="Convert CVAT to VIA")
    cvat_via_parser.add_argument("--input_dir", required=True, help="Directory with CVAT XML file")
    cvat_via_parser.add_argument("--output_dir", default="dst", help="Output directory for VIA files")
    
    # CVAT to YOLO
    cvat_yolo_parser = subparsers.add_parser("cvat-to-yolo", help="Convert CVAT to YOLO")
    cvat_yolo_parser.add_argument("--input_dir", required=True, help="Directory with CVAT XML file")
    cvat_yolo_parser.add_argument("--output_dir", default="dst", help="Output directory for YOLO files")
    
    # YOLO to VOC
    yolo_voc_parser = subparsers.add_parser("yolo-to-voc", help="Convert YOLO to Pascal VOC")
    yolo_voc_parser.add_argument("--input_dir", required=True, help="Directory with YOLO files")
    yolo_voc_parser.add_argument("--output_dir", default="dst", help="Output directory for VOC files")
    
    # VOC to COCO
    voc_coco_parser = subparsers.add_parser("voc-to-coco", help="Convert Pascal VOC to COCO")
    voc_coco_parser.add_argument("--input_dir", required=True, help="Directory with VOC XML files")
    voc_coco_parser.add_argument("--output_file", required=True, help="Output COCO JSON file")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
        
    if args.command == "labelme-to-coco":
        labelme_to_coco(args.input_dir, args.output_file)
    elif args.command == "labelme-to-yolo":
        labelme_to_yolo(args.input_dir, args.output_dir)
    elif args.command == "labelme3-to-labelme":
        labelme3_to_labelme(args.input_dir, args.output_dir)
    elif args.command == "labelme3-to-via":
        labelme3_to_via(args.input_dir, args.output_dir)
    elif args.command == "via-to-labelme3":
        via_to_labelme3(args.input_dir, args.output_dir)
    elif args.command == "cvat-to-via":
        cvat_to_via(args.input_dir, args.output_dir)
    elif args.command == "cvat-to-yolo":
        cvat_to_yolo(args.input_dir, args.output_dir)
    elif args.command == "yolo-to-voc":
        yolo_to_voc(args.input_dir, args.output_dir)
    elif args.command == "voc-to-coco":
        voc_to_coco(args.input_dir, args.output_file)


if __name__ == "__main__":
    main()
