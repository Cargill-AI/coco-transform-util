
import os
if os.getcwd().split('/')[-1] == 'samples':
    os.chdir('../')
elif os.getcwd().split('/')[-1] == 'coco-transform-util':
    pass
print('Current Working Dir for the Code:', os.getcwd())

import cv2
import glob
import json
import random
import ctu

def run():

    paths = glob.glob('example_data/*.jpg')
    if len(paths)==0:
        raise Exception(f'No Image detected in the directory: {os.getcwd()}/example_data/')
    paths.sort()

    path = paths[2]#[random.randint(0,len(paths))]

    ## reading the image
    modif_di = {
        'image_path': path,
        'aspect_ratio': 'dont maintain',
        # "options: None, 'maintain', 'dont maintain'",
        'image_ht_wd': (1000, 1500),
        # (1500, 2000),
        'padding_ht_wd': None,# (0.15,0.15),
        # 'eg: None, (0.15,0.15)',
        'padding_color': (10, 10, 10),
        'crop_pt1_pt2': ((0.25,0.25), (0.75,0.75)),
        # 'eg: None, ((0.1,0.1), (0.9,0.9))'
    }

    modif_di = ctu.accept_and_process_modif_di(modif_di)
    img = ctu.get_modif_image(modif_di)
    anno = ctu.get_modif_coco_annotation(img, coco_path, modif_di)

    ctu.Visualize.draw_annotation(
        img,
        coco_ann_di=anno,
        cls_mapper_di=None,
        draw_what=['mask'], # 'bbox', 'polyline', 
        thickness=10
    )

    # print(anno)

    ## creating a mask
    poly = anno['annotations'][0]['segmentation']
    mask = ctu.create_mask(img, poly, transparent_mask=True)
    aml.viewImage(mask)

    mask = ctu.create_mask(img, poly, transparent_mask=False)
    aml.viewImage(mask)
    
    
if __name__=='__main__':
    run()
