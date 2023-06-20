# cvat2via

tool convert cvat annotation `CVAT for images 1.1` and via-via 2.0 annotation `via_region_data.json`

# usages

- convert cvat annotation `CVAT for images 1.1` to via-via 2.0 annotation `via_region_data.json`
- convert via-via 2.0 annotation `via_region_data.json` to cvat annotation `CVAT for images 1.1`

# guide

# TODOs

- `labelImg`

# dataset structure

**cvat**

        cvat
        ├── annotations.xml
        └── images
            ├── img2.jpg
            ├── img3.jpg
            └── img.jpg 

**via**

        via
        ├── img2.jpg
        ├── img3.jpg
        ├── img.jpg
        ├── via_region_data.csv
        └── via_region_data.json

# references

https://www.geeksforgeeks.org/create-xml-documents-using-python/

https://www.geeksforgeeks.org/read-json-file-using-python/

https://www.geeksforgeeks.org/xml-basics/

https://github.com/heartexlabs/labelImg