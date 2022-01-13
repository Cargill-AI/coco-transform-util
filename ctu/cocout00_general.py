
import cv2
import amleet as aml
from copy import deepcopy
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

    print( 'Following Setting is being used:\n\t'+
          '\n\t'.join([ f'{k}\t: {item}' for k,item in modif_step_di.items() ]))
    
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
            img = aml.FrameManipulate.resize_with_aspect_ratio(
                img, width=c_di['image_ht_wd'][1])
        else:
            img = cv2.resize(
                img, c_di['image_ht_wd'][::-1], interpolation = cv2.INTER_AREA)

    ## 3. Add padding
    if c_di['padding_ht_wd'] is not None:
        img = add_relative_padding_to_image(
            img, rel_padding_ht_wd=c_di['padding_ht_wd'], pad_color=c_di['padding_color'])

    ## 4. Crop
    if c_di['crop_pt1_pt2'] is not None:
        img = aml.FrameManipulate.relative_size_based_crop(
            img, rel_pt1=c_di['crop_pt1_pt2'][0], rel_pt2=c_di['crop_pt1_pt2'][1])
        
    return img


def get_modif_coco_annotation(img, coco_path, modif_step_di):
    '''
    '''
    c_di = modif_step_di
    
    ## 1. Get this Annotation from local
    coco_ann_di = WholeCoco2SingleImgCoco( annotation_path=coco_path, coco_di=None
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
    final_ann_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=img.shape[:2])
    
    return final_ann_di



# ---------------------------------------------------------------------------------------------------------- #

def add_relative_padding_to_image(img, rel_padding_ht_wd=(0.15,0.15), pad_color=(10,10,10)):
    ''' ------------------------------------------------------------------------------------<<< Add this in the COCO2COCOREL Code
    Image will be kept at the center and equivalent size of padding 
    will be added on two sides
    '''
    scht, scwd = img.shape[:2]
    extra_x, extra_y = int(scht*rel_padding_ht_wd[0]), int(scwd*rel_padding_ht_wd[1])
    top, bottom = extra_x, extra_x
    left, right = extra_y, extra_y

    pdd_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, 
                                 value=pad_color)
    return pdd_img



## Draw the annotation on Image
def show_img_with_annotation(img, coco_ann_di=None, cls_mapper_di=None, 
                             draw_what=['bbox', 'polyline', 'mask'], thickness=10):
    ''' 
        draw_what = ['polyline', 'bbox', 'mask' ]
        cls_mapper_di = {
            '0': 'reference_object',
            '1': 'orange',
            '2': 'carrot',
            '3': 'potato'
        }
    '''
    draw_im = img.copy()
    color_di = {}
    
    if coco_ann_di is not None:
        for ann in coco_ann_di['annotations']:

            ## assign and get color for the class
            if cls_mapper_di is None:
                clr = aml.ColorConvRand().random()
                color = clr.rgb
            else:
                cls = str(ann['category_id'])
                clr = aml.ColorConvRand().random()
                color = clr.rgb
                
                ## if already assigned then pick that color
                if cls in color_di.keys():
                    color = color_di[cls]
                else:
                    color_di[cls] = color

            ## draw what ever is asked
            pol = aml.Polygons.create(ann['segmentation'])
            if 'bbox' in draw_what:
                bb = pol.proj_to_bbox()
                draw_im = bb.draw(image=draw_im, color=color, thickness=thickness)

            if 'polyline' in draw_what:
                draw_im = pol.draw(image=draw_im, color=color, thickness=thickness)

            if 'mask' in draw_what:
                msk = pol.proj_to_mask(width=img.shape[1], height=img.shape[0])
                # mask_as_array = msk.array
                draw_im = msk.draw(image=draw_im, color=color)
        
    ## Show the Image
    aml.viewImage(draw_im, show_in_rgb=True, input_color_space='bgr')

    
    



    
    
    
    