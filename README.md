# 2label

tool convert annotations

# usages

- convert cvat annotation `CVAT for images 1.1` to via-via 2.0 annotation `via_region_data.json`
- convert via-via 2.0 annotation `via_region_data.json` to cvat annotation `CVAT for images 1.1`

# guide

# TODOs

- `cvat_via.py` ✔
- `cvat_labelme.py` ✗
- `labelme_via.py` ✗
- `via_labelme.py` ✗
  
# Annotation tools

- `labelImg`
- `labelme`
- `PixelAnnotationTool`

*Note:*
- `labelImg` only support rectangle annotation.
- `labelme` support polygon annotation and rectangle annotation.
- `cvat` support polygon annotation and rectangle annotation and line annotation.
- annotations in via attribute is `labels`
# references

https://github.com/heartexlabs/labelImg

https://github.com/wkentaro/labelme

https://github.com/abreheret/PixelAnnotationTool

https://www.geeksforgeeks.org/create-xml-documents-using-python/

https://www.geeksforgeeks.org/read-json-file-using-python/

https://www.geeksforgeeks.org/xml-basics/
