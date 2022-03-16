# coco-transform-util
A python package to perform same transformation to coco-annotation as performed on the image.


## Installation

### Way 1
```bash
$ git clone https://github.com/Cargill-AI/coco-transform-util.git
$ cd coco-transform-util
$ python3 setup.py install
```

### Way 2
```bash
$ pip3 install git+https://github.com/Cargill-AI/coco-transform-util.git
<<< Username: <user_id or email>
<<< Password: <personal access token or SSH key>
```
Personal Access token looks like this `83b318cg875a5g302e5fdaag74afc8ceb6a91a2e`.

Reference: [How to generate Personal Access token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)  

### Check installation
```python
import ctu
print(ctu.__version__)
```


## Benefits and Use Cases

1. Faster Model Training: Decrease the size of images and accordingly its annotation will be changed using this.  
2. Flexibility: Rescaling of images and annotations to meet the need of Model/Framework.  
3. Cost Saving: Lesser Computation requirement as images can be downscaled.  
4. Interpretability: Annotation Visualization is also a part of this package.
5. Data Augmentation: \<more practical in future\>
6. Ability to handle other cases: Added Functionality such as cropping or padding of the annotation can help in multiple other cases such as:
    - cropping out each object image & annotation from an original image
    - cropping unnecessary area to zoom in on some particular area.
    - converting images to 1:1 aspect ratio by using padding and/or cropping.
  
  
## How to use it?
  
### Core
There are four core modules inside that helps in performing operations on COCO Annotation. These can imported as shown below:  
```python
from ctu import WholeCoco2SingleImgCoco, Coco2CocoRel, CocoRel2CocoSpecificSize, AggreagateCoco  
```  
It's recommended that you have look at `samples/example_core_modules.py` to understand and explore how to use these.
  
### Wrapper
Making use of wrappers can also come in handly to perform multiple operations in a much simpler and interpretable manner using the functions provided below:  
```python
from ctu import (
    sample_modif_step_di, get_modif_imag, get_modif_coco_annotation, 
    accept_and_process_modif_di, ImgTransform, Visualize
)
```
It's recommended that you have look at `samples/example_highlevel_function.py` to understand and explore how to use these. 
  
  
Some sample data has also been provided with this package at `example_data/*` to explore these functionalities.  
  
  
## Demo / Sample

A sample HTML created from Jupyter-Notebook, contating some sample results has been added to the path `samples/Demo-SampleOutput.html`.  
  
  
## Version History

- v0.1: Core Modules: `WholeCoco2SingleImgCoco, Coco2CocoRel, CocoRel2CocoSpecificSize`. External Dependency on AMLEET package.
- v0.2: Removed the dependency on AMLEET package. Develop Core Module: `AggreagateCoco`. Addition of field "area" under "annotations" in coco.
- v0.3: Completed: Remove the out of frame coordinates in annotation. Update & add fields in "annotation" \> "images". Ability to create transparent and general mask `create_mask`. **In Development:** Ability to export transformed image, mask and annotation per image wise and as a whole too. 

  
## Future  
- Update the image fields in "images" key. (done)
- Crop out the annotation which are out-of-frame based on recent image shape. (done)
- Annotation Visualization + Mask creation can become a core feature to this library. (done)
- Rotate 90 degree left/right.  
- Flip horizontally or vertically. 
- COCO to other annotation format can also be a feature to this package.

## Push to pypi
```bash
$ python3 setup.py sdist
$ twine upload dist/*
```




