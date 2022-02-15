
import cv2
from copy import deepcopy
from ctu.cocout00_utils import ImgTransform
from ctu.cocout01_slicer import WholeCoco2SingleImgCoco
from ctu.cocout02_invariant_format import Coco2CocoRel
from ctu.cocout03_inv_to_coco import CocoRel2CocoSpecificSize


sample_modif_step_di = {
    'image_path': '<add path to a image>',
    'aspect_ratio': "options: None, 'maintain', 'dont maintain'",
    'image_ht_wd': (1500,2000),
    'padding_ht_wd': "eg: None, (0.15,0.15)",
    'padding_color': (10,10,10),
    'crop_pt1_pt2': 'eg: None, ((0.1,0.1), (0.9,0.9))',
}

def accept_and_process_modif_di(modif_step_di):
    '''
    modif_step_di = {
        'image_path': paths[random.randint(0,len(paths)-1)],
        'aspect_ratio': aspect_ratio[random.randint(0,len(aspect_ratio)-1)],
        'image_ht_wd': size_ht_wd_li[random.randint(0,len(size_ht_wd_li)-1)],
        'padding_ht_wd': pad_ht_wd_li[random.randint(0,len(pad_ht_wd_li)-1)],
        'padding_color': (40,40,40),
        'crop_pt1_pt2': crop_pt1_pt2_li[random.randint(0,len(crop_pt1_pt2_li)-1)],
    }
    '''
    modif_step_di = deepcopy(modif_step_di)
    ## check for values consistencies

    ## process
    if modif_step_di['aspect_ratio'] is None: modif_step_di['image_ht_wd'] = None
    if modif_step_di['aspect_ratio'] == 'maintain':
        # my_dict.pop('key', None)
        modif_step_di['image_ht_wd'] = ('-',modif_step_di['image_ht_wd'][1])
    modif_step_di['img_name'] = modif_step_di['image_path'].split('/')[-1]

    print('Following Setting is being used:\n\t'+
          '\n\t'.join([ f'{k}\t: {item}' for k,item in modif_step_di.items()]))

    return modif_step_di


def get_modif_image(modif_step_di):
    '''
    '''
    c_di = modif_step_di
    ## manipulate image

    ## 1. Read
    img = cv2.imread(c_di['image_path'])

    ## 2. Size change
    if c_di['image_ht_wd'] is not None:
        if c_di['aspect_ratio']=='maintain':
            img = ImgTransform.resize_with_aspect_ratio(
                img, width=c_di['image_ht_wd'][1])
        else:
            img = cv2.resize(
                img, c_di['image_ht_wd'][::-1], interpolation = cv2.INTER_AREA)

    ## 3. Add padding
    if c_di['padding_ht_wd'] is not None:
        img = ImgTransform.add_relative_padding_to_image(
            img, rel_padding_ht_wd=c_di['padding_ht_wd'], pad_color=c_di['padding_color'])

    ## 4. Crop
    if c_di['crop_pt1_pt2'] is not None:
        img = ImgTransform.relative_size_based_crop(
            img, rel_pt1=c_di['crop_pt1_pt2'][0], rel_pt2=c_di['crop_pt1_pt2'][1])

    return img


def get_modif_coco_annotation(img, coco_path, modif_step_di):
    '''
    '''
    c_di = modif_step_di

    ## 1. Get this Annotation from local
    coco_ann_di = WholeCoco2SingleImgCoco(
        annotation_path=coco_path, coco_di=None
        ).run(modif_step_di['img_name'])

    if coco_ann_di is None:
        return None

    ## 2. Modify Invariant Annotation
    rel_coco_di = Coco2CocoRel().run(
        coco_ann_di,
        offset=('orig_to_pad' if c_di['padding_ht_wd'] is not None else None),
        rel_padding_ht_wd=c_di['padding_ht_wd'],
        rel_crop_pt1_pt2=c_di['crop_pt1_pt2']
    )

    ## 3. convert it to coordinate format
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2],
                                                  crop_oof=True, area_thresh_for_oof=0)

    return final_ann_di


# ---------------------------------------------------------------------------------------------------------- #

