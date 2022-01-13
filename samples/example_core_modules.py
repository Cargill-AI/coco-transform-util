
import os
if os.getcwd().split('/')[-1] == 'samples':
    os.chdir('../')
elif os.getcwd().split('/')[-1] == 'coco-transform-util':
    pass
print('Current Working Dir for the Code:', os.getcwd())

import cv2
import glob
import random
import amleet as aml
from ctu import WholeCoco2SingleImgCoco, Coco2CocoRel, CocoRel2CocoSpecificSize
from ctu import add_relative_padding_to_image, show_img_with_annotation


def run():
    ## configs
    coco_path= 'example_data/coco-annotation.json'
    paths = [ f for f in glob.glob('example_data/*') if f.split('.')[-1] in ['jpeg', 'png', 'jpg'] ]

    ## getting image address
    path = paths[random.randint(0,len(paths)-1)]
    img_name = path.split('/')[-1]


    # ----------------------------- < Original

    ## reading the image
    img = cv2.imread(path)

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None).run(img_name)

    ## draw with annotation
    print('\nOriginal')
    show_img_with_annotation(img, coco_ann_di)


    # ----------------------------- < Rescaling image size (With Aspect Ratio)

    ## reading the image
    img = cv2.imread(path)
    img = aml.FrameManipulate.resize_with_aspect_ratio(img, width=1000)

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print('\nRescaling image size (With Aspect Ratio)')
    show_img_with_annotation(img, final_ann_di)

    # ----------------------------- < Rescaling image size (Without Aspect Ratio)

    wd_ht = (2000,1000)

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print('\nRescaling image size (Without Aspect Ratio)')
    show_img_with_annotation(img, final_ann_di)


    # ----------------------------- < Rescaling image size + add padding to the image

    wd_ht = (1000,1000)
    padding_htwd = (0.55,0.15)

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)
    img = add_relative_padding_to_image(img, rel_padding_ht_wd=padding_htwd, pad_color=(40,40,40))

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di, offset='orig_to_pad', rel_padding_ht_wd=padding_htwd )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print('\nRescaling image size + add padding to the image')
    show_img_with_annotation(img, final_ann_di)


    # ----------------------------- < Rescaling image size + cropping the imagee & maintaing the annotation

    wd_ht = (1000,1000)
    crop_rel_pt1_pt2 = ((0.5,0.0), (1.0,0.75))

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)
    # img = add_relative_padding_to_image(img, rel_padding_ht_wd=padding_htwd, pad_color=(40,40,40))
    img = aml.FrameManipulate.relative_size_based_crop(img, rel_pt1=crop_rel_pt1_pt2[0], rel_pt2=crop_rel_pt1_pt2[1])

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di, offset=None, rel_crop_pt1_pt2=crop_rel_pt1_pt2 )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print('\nRescaling image size + cropping the imagee & maintaing the annotation')
    show_img_with_annotation(img, final_ann_di)


    # ----------------------------- < Rescaling image size + add padding to the image + cropping the imagee & maintaing the annotation

    wd_ht = (1000,1000)
    padding_htwd = (0.55,0.15)
    crop_rel_pt1_pt2 = ((0.5,0.0), (1.0,0.75))

    ## reading the image & changing the size
    img = cv2.imread(path)
    img = cv2.resize(img, wd_ht, interpolation = cv2.INTER_AREA)
    img = add_relative_padding_to_image(img, rel_padding_ht_wd=padding_htwd, pad_color=(40,40,40))
    img = aml.FrameManipulate.relative_size_based_crop(img, rel_pt1=crop_rel_pt1_pt2[0], rel_pt2=crop_rel_pt1_pt2[1])

    ## annotaion for the same
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None).run(img_name)
    rel_coco_di = Coco2CocoRel().run( coco_ann_di, offset='orig_to_pad', rel_padding_ht_wd=padding_htwd, rel_crop_pt1_pt2=crop_rel_pt1_pt2 )
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])

    ## draw with annotation
    print('\nRescaling image size + add padding to the image + cropping the imagee & maintaing the annotation')
    show_img_with_annotation(img, final_ann_di)

    # ----------------------------------------------------------------------------------------------------------- #

if __name__=='__main__':
    run()
