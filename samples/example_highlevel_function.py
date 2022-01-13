
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
from ctu import (
    sample_modif_step_di, accept_and_process_modif_di, 
    get_modif_image, get_modif_coco_annotation
)
from ctu import Visualize, AggreagateCoco

def run():
    coco_path= 'example_data/coco-annotation.json'
    paths = [ f for f in glob.glob('example_data/*') if f.split('.')[-1] in ['jpeg', 'png', 'jpg'] ]
    if len(paths)==0:
        raise Exception(f'No Image detected in the directory: {os.getcwd()}/example_data/')
    
    ## configs
    counter, limit = 0, 5
    aspect_ratio = [ None, 'maintain', 'dont maintain']  # None = original
    size_ht_wd_li = [ (500,500), (1000,3000), (3000,1000) ]  # when aspect ratio is to be maintain, only width will be considered
    pad_ht_wd_li = [ None, (0.15,0.15), (0.5,0.1), (0.1,0.5) ]
    crop_pt1_pt2_li = [ None, ((0.5,0.0), (1.0,0.75)), ((0.0,0.0), (1.0,0.5)) ]
    same_color_for_class = True

    
    cls_mapper_di = {
        '1':'coffee-bean',
        '2':'tea-seed',
        '3':'mango',
        '4':'lemon',
        '5':'orange'
    } if same_color_for_class else None
    
    temp_dir = './temporary/'
    if not os.path.exists(temp_dir): os.mkdir(temp_dir) # new
    annotation_li = []  # new
    while counter<limit:

        print('-'*100)
        print(f'Counter: {counter} \n')
        check_di = sample_modif_step_di

        check_di['image_path'] = paths[random.randint(0,len(paths)-1)]
        check_di['aspect_ratio'] = aspect_ratio[random.randint(0,len(aspect_ratio)-1)]
        check_di['image_ht_wd'] = size_ht_wd_li[random.randint(0,len(size_ht_wd_li)-1)]
        check_di['padding_ht_wd'] = pad_ht_wd_li[random.randint(0,len(pad_ht_wd_li)-1)]
        check_di['crop_pt1_pt2'] = crop_pt1_pt2_li[random.randint(0,len(crop_pt1_pt2_li)-1)]

        modif_di = accept_and_process_modif_di(check_di)
        img = get_modif_image(modif_di)
        print('Image Shape: ', img.shape)

        anno = get_modif_coco_annotation(img, coco_path, modif_di)
        
        ## Save Image Locally and change the image name in the annotation
        img_new_name = f'./temporary/file_{counter}.jpeg'
        cv2.imwrite(img_new_name, img)
        print('New Image Saved:', img_new_name.split('/')[-1])
        anno['images'][0]['file_name'] = img_new_name.split('/')[-1]
        
        coco_new_path = f'./temporary/coco_annotation_file_{counter}.json'
        with open(coco_new_path, 'w') as f:
            json.dump(anno, f) #, indent=4


        annotation_li.append(anno)  # new
        
        Visualize.draw_annotation(img, anno, cls_mapper_di=cls_mapper_di, draw_what=['polyline', 'mask'])

        counter += 1
    
    ## Aggregate Coco Annotations
    print('# of Individual Annotations: ', len(annotation_li))
    print('Aggregating Individual Annotations....')
    agg_coco_di = AggreagateCoco(annotation_li).run(if_img_name_match='append', show_warning='True')
    print('.... Complete !!!')
    print('# of Images in aggregated Anno:', len(agg_coco_di['images']))
    print('# of Annotation in aggregated Anno:', len(agg_coco_di['annotations']))
    
    coco_new_path = './temporary/coco_annotation.json'
    with open(coco_new_path, 'w') as f:
        json.dump(agg_coco_di, f, indent=4)
    print('Annotation Saving Location:',coco_new_path)
    
    return agg_coco_di
    
    
if __name__=='__main__':
    run()
