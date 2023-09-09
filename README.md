# 2label
tool convert annotations

![draft](assets/diagram.png)

# usages
- convert cvat annotation `CVAT for images 1.1` to via-via 2.0 annotation `via_region_data.json`
- convert via-via 2.0 annotation `via_region_data.json` to cvat annotation `CVAT for images 1.1`

# functions
- convert
- utils
  + cutting tool
  + convert tfrecord
  + augment data 
  
# Annotation tools
- [labelImg](https://github.com/heartexlabs/labelImg) install command: `pip install labelImg`
- [labelme](https://github.com/wkentaro/labelme) install command: `pip install labelme`
- [PixelAnnotationTool](https://github.com/abreheret/PixelAnnotationTool)
- [cvat](https://github.com/opencv/cvat)
- [via](https://www.robots.ox.ac.uk/~vgg/software/via/)
*Note:*
- `labelImg` only support rectangle annotation.
- `labelme` support polygon annotation and rectangle annotation.
- `cvat` support polygon annotation and rectangle annotation and line annotation.
- annotations in via attribute is `labels`

# references