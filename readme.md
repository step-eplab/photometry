### Example of ../paths.json:

{\
"dir_raw_images": "/STEP/main/data/F3/images/",\
"dir_res": "/STEP/main/data/F3/result/",\
"dir_configs": "/STEP/main/configs/F3/",\
"dir_cat": "/STEP/main/catalogs/F3/",\
"cat_name": "F3.list"
}

paths to directories with folders of nights (format: dd.mm.yy):
* dir_raw_images: with raw data
* dir_res: for results

to configs
* dir_configs

to GAIA catalog created by create_cat.py module in preparation package
* dir_cat 
* cat_name\
catalog_path = dir_cat + cat_name
