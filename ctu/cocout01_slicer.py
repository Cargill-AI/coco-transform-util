
import json
from copy import deepcopy


class WholeCoco2SingleImgCoco:
    '''
    Accepts both coco and coco relative annotation
    Coco Annotation Slicer: Works Coco with Relative Annotation too
    Create coco annotation per image wise. Lookup will be based on index
    '''
    @classmethod
    def read_annotation(cls, annotation_path):
        with open(annotation_path, 'r') as file:
            coco_ann_di = json.load(file)
        return coco_ann_di

    def __init__(self, annotation_path=None, coco_di=None, inplace=False, msg=False):
        '''
        Precedance to "annotation_path" is given
        '''
        self.msg = msg

        ## Read Annotation File
        if annotation_path is not None:
            if self.msg: print('Annotation Path is used to generate annotation.')
            self.coco_ann_di = self.read_annotation(annotation_path)
        else:
            if self.msg: print('Provideed Annotation is used to generate annotation.')
            self.coco_ann_di = coco_di if inplace else deepcopy(coco_di)

    def run(self, img_index_or_name, index_type='general_index'):
        '''
        Input:
            img_index_or_name: identifier to look for image
                if integer then work as index
                if string then work as image name
            index_type: 'coco_image_id' or 'general_index'
        Return:
            Single imagee coco annotation
        '''
        ## get whole coco di
        cdi = self.coco_ann_di

        ## find matching information
        if (img_index_or_name is not None):
            if isinstance(img_index_or_name, str):  # image name is provided
                im_matching_ind = [i for i,e in enumerate(cdi['images'])
                                   if e['file_name']==img_index_or_name]
                if len(im_matching_ind)>1: 
                    print('Trying to locate:', img_index_or_name)
                    print('Matched Index:', im_matching_ind)
                    raise Exception('[Err1a] 2 or more images share the image name.'
                                    ' Check your annotation')
                elif len(im_matching_ind)==0:
                    print('No Matching Index for image_name:', img_index_or_name)
                    return None
                im_matching_ind = im_matching_ind[0]
                img_id = cdi['images'][im_matching_ind]['id']
            else:
                index = img_index_or_name

                ## Index based lookup
                if index_type=='coco_image_id':
                    img_id = index
                    im_matching_ind = [i for i,e in enumerate(cdi['images']) if e['id']==img_id]
                    if len(im_matching_ind)>1:
                        print('Trying to locate:', img_id)
                        print('Matched Index:', im_matching_ind)
                        raise Exception('[Err2a] 2 or more images share the image index.'
                                        ' Check your annotation')
                    elif len(im_matching_ind)==0:
                        print('No Matching Index for image_id:', img_id)
                        return None
                    im_matching_ind = im_matching_ind[0]
                else:
                    im_matching_ind = index
                    img_id = cdi['images'][index]['id']
        else:
            raise Exception('Either Image name or index in coco["images"] list or '
                  'ID of image in coco["images"] needs to be provided')

        ## getting matching annotation for this image
        anno_matching_ind = [i for i,e in enumerate(cdi['annotations']) if e['image_id']==img_id ]

        ## genrating single inage coco
        indi_di = {}
        indi_di['info'] = cdi['info']
        indi_di['images'] = [cdi['images'][im_matching_ind]]  # single element in list
        indi_di['annotations'] = [cdi['annotations'][e] for e in anno_matching_ind]
        indi_di['categories'] = cdi['categories']

        return indi_di


''' ## Sample Code
coco_path= 'data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json'

## Reading whole annotation from a path
whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)

## (1) Create annotation for single image: (1) Using already read coco_di
single_coco_di = WholeCoco2SingleImgCoco(annotation_path=coco_path).run(0)
print(single_coco_di)

## (1) Create annotation for single image: (2) Using the path
single_coco_di = WholeCoco2SingleImgCoco(coco_di=whole_anno_di).run(0)
print(single_coco_di)

## (2) Create annotation for single image: (1) Image selection Based on Image Index present in List
single_coco_di = WholeCoco2SingleImgCoco(coco_path).run(0, index_type='general_index')
print(single_coco_di)  # observe images: id will be+1 to index by default

## (2) Create annotation for single image: (2) Image selection Based on Image ID (present in coco)
single_coco_di = WholeCoco2SingleImgCoco(coco_path).run(1, index_type='coco_image_id')
print(single_coco_di)

## (2) Create annotation for single image: (3) Image selection Based on Image Name
single_coco_di = WholeCoco2SingleImgCoco(coco_path).run('IMG_20210302_102203_wt98.jpg')
print(single_coco_di)

## (3) Create annotation for single image: (1) Using Coco Annotation
single_coco_di = WholeCoco2SingleImgCoco(coco_di=whole_anno_di).run(0)
print(single_coco_di)

## (3) Create annotation for single image: (2) Using Relative Coco Annotation
rel_coco_di = Coco2CocoRel().run(whole_anno_di)
# print(rel_coco_di)
single_coco_di = WholeCoco2SingleImgCoco(coco_di=rel_coco_di).run(0)
print(single_coco_di)
# '''

