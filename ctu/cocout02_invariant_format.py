
from copy import deepcopy
from ctu.cocout01_slicer import WholeCoco2SingleImgCoco


class Coco2CocoRel:
    ''' Convert General Coco annotation to relative coordinate 
    "area" is droppd in this format.
    '''

    def __init__(self, msg=False):
        self.msg = msg

    ## convert coordinate to relative values
    def _is_x_coord(self, index):
        return index%2==0

    def _gen_relative_coordinate_li(self, coordinate_li, img_width, img_height):
        '''
        coordinate_li: [3386.5929339477707, 1049.7572964669732, 97.52380952380963, 1049.1674347158212]
        to relative: [0.7349377026796378, 0.3037492177277122, 0.021164021164021187, 0.30357854013767976]
        '''
        if (len(coordinate_li)>1) and (max(coordinate_li)<=1):
            print('Data is already scaled to relative dimensions')
            return coordinate_li
        return [
            coordinate/img_width if self._is_x_coord(i) else coordinate/img_height
            for i,coordinate in enumerate(coordinate_li)
        ]

    def _transform_one_image_info(self, image_info):
        ''' works on a element '''
        image_info['orig_width'] = image_info['width']
        image_info['orig_height'] = image_info['height']
        return image_info

    def _transform_one_annotation(self, image_info, anno_info):
        ''' works on a element '''
        img_wd, img_ht = image_info['width'], image_info['height']
        # print(anno_info.keys())
        anno_info['segmentation'] = [self._gen_relative_coordinate_li(anno, img_wd, img_ht)
                                     for anno in anno_info['segmentation']]
        anno_info['bbox'] = self._gen_relative_coordinate_li(anno_info['bbox'], img_wd, img_ht)

        ## Delete area key
        anno_info.pop('area', None)

        return anno_info

    def gen_coco_rel_anno(self, coco_ann_di):
        ''' '''
        if self.msg:
            print('Following keys are present in coco annotation:', list(coco_ann_di.keys()))
            print('Note: "area" will been dropped from "annotations" as it hasn\'t been converted to relative measure')

        for i,k in enumerate(coco_ann_di['annotations']):
            # cls_info = coco_ann_di['categories'][i]
            anno_info = coco_ann_di['annotations'][i]

            # image_index = anno_info['image_id'] - 1
            image_index = [i for i,e in enumerate(coco_ann_di['images'])
                           if e['id']==anno_info['image_id']][0]

            ## image info
            image_info = coco_ann_di['images'][image_index]

            ## edit annootation
            coco_ann_di['annotations'][i] = self._transform_one_annotation(
                image_info, anno_info)

            ## image info
            coco_ann_di['images'][image_index] = self._transform_one_image_info(image_info)

        return coco_ann_di

    ## -------------------------------------------------------< Related to Offset (Start)

    def convert_coord_from_orig_to_pad_addition(
        self, old_rel_x=None, old_rel_y=None, rel_padding_ht_wd=(0.35, 0.35)
    ):
        '''
        Desc: takes the old relative coordinate and converts to new as padding is added.
              (Image Sizeee is Increased)


        will be used for offsetting the coordinate the image which is inside the padded image
        This padding was added on both sides

        padded_img:

        new origin (0,0)
            +-------------------------------+ --      ---
            |*******************************| pady    
            |*    old +-----------+*********| --      
            |* origin |           |*********|         
            |*********|           |*********| old_ht   new_ht
            |*********+-----------+ rel_pt2*| --
            |*******************************| pady    
            +-------------------------------+ --      --
            |  padx   |  old_wd   |   padx  | (When Pad is added)
            |            new_wd             |

            ## New and old will both be 1 in relative coordinate


      Dimension Change:

              Initial Origin       Initial End
                      O-----------|

             pad relative to old added on both side
            |---------O-----------|---------|

            New Origin                    New End (New coord relative to this new origin and length)
            O---------|-----------|---------|


        eg. Input: old_rel_x=0.5, old_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5)
            Output: (0.5, 0.5)
        '''
        if ((old_rel_x is None) and (old_rel_y is None)):
            raise Exception('Both the "old_rel_x" and "old_rel_y" can\'t be None')
        pady, padx = rel_padding_ht_wd
        ## calculating the new rel_x after padding was added based on previous rel_x
        rx = ((padx + old_rel_x) / (1+2*padx)) if old_rel_x is not None else None
        ry = ((pady + old_rel_y) / (1+2*pady)) if old_rel_y is not None else None

        if (rx is not None) and (ry is not None):
            return rx, ry
        elif (rx is not None) and (ry is None):
            return rx
        elif (rx is None) and (ry is not None):
            return ry

    '''
    self=1
    convert_coord_from_orig_to_pad_addition(self, old_rel_x=0.5, old_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5))
    # (0.5, 0.5)
    convert_coord_from_orig_to_pad_addition(self, old_rel_x=0, old_rel_y=1, rel_padding_ht_wd=(0.5, 0.5))
    # (0.25, 0.75)
    '''

    def convert_coord_from_pad_to_orig(
        self, pad_rel_x=None, pad_rel_y=None, rel_padding_ht_wd=(0.35, 0.35)
    ):
        '''
        Desc: takes the old relative coordinate when the padding was useed and converts it 
              to that of the original . (Image Size is Decreased)

        Note: "rel_padding_ht_wd" is still according to the very initail point when it was added

        Dimension Change:

               Old Origin                    Old End
                O---------|-----------|---------|

             pad relative to old added on both side
                |---------O-----------|---------|

            back to Initial Origin       Initial End
                          O-----------|


        eg. Input: old_rel_x=0.5, old_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5)
            Output: (0.5, 0.5)
        '''
        if ((pad_rel_x is None) and (pad_rel_y is None)):
            raise Exception('Both the "pad_rel_x" and "pad_rel_y" can\'t be None')
        pady, padx = rel_padding_ht_wd

        ## calculating the very old rel_x before padding was added based on the rel_x from the padded img
        old_rel_x = (pad_rel_x * (1+2*padx) - padx) if pad_rel_x is not None else None
        old_rel_y = (pad_rel_y * (1+2*pady) - pady) if pad_rel_y is not None else None

        if (old_rel_x is not None) and (old_rel_y is not None):
            return old_rel_x, old_rel_y
        elif (old_rel_x is not None) and (old_rel_y is None):
            return old_rel_x
        elif (old_rel_x is None) and (old_rel_y is not None):
            return old_rel_y

    '''
    self=1
    convert_coord_from_pad_to_orig(self, pad_rel_x=0.5, pad_rel_y=0.5, rel_padding_ht_wd=(0.5, 0.5))
    # (0.5, 0.5)
    convert_coord_from_pad_to_orig(self, pad_rel_x=0, pad_rel_y=1, rel_padding_ht_wd=(0.5, 0.5))
    # (-0.5, 1.5)  ## mean the coordinate is in the padding region
    '''

    def _offset_one_annotation(self, anno_info, offset='orig_to_pad', rel_padding_ht_wd=(0.35, 0.35)):
        ''' works on a element '''
        o2p = self.convert_coord_from_orig_to_pad_addition
        p2o = self.convert_coord_from_pad_to_orig

        if offset in ['orig_to_pad', 'pad_to_orig']:

            ## converting segmentation
            anno_info['segmentation'] = [[
                p2o(
                    pad_rel_x=(e if self._is_x_coord(i) else None),
                    pad_rel_y=(None if self._is_x_coord(i) else e),
                    rel_padding_ht_wd=rel_padding_ht_wd
                ) if offset=='pad_to_orig' else o2p(
                    old_rel_x=(e if self._is_x_coord(i) else None),
                    old_rel_y=(None if self._is_x_coord(i) else e),
                    rel_padding_ht_wd=rel_padding_ht_wd
                )
                for anno in anno_info['segmentation']
                for i,e in enumerate(anno)
            ]]

            ## converting bbox
            anno_info['bbox'] = [
                p2o(
                    pad_rel_x=(e if self._is_x_coord(i) else None),
                    pad_rel_y=(None if self._is_x_coord(i) else e),
                    rel_padding_ht_wd=rel_padding_ht_wd
                ) if offset=='pad_to_orig' else o2p(
                    old_rel_x=(e if self._is_x_coord(i) else None),
                    old_rel_y=(None if self._is_x_coord(i) else e),
                    rel_padding_ht_wd=rel_padding_ht_wd
                )
                for i,e in enumerate(anno_info['bbox'])
            ]

        else:
            raise Exception('Unacceptatble value for "offset"')

        return anno_info

    def offset_whole_coco_annotation(
        self, coco_anno_di, offset='orig_to_pad', rel_padding_ht_wd=(0.35, 0.35)
    ):
        '''
        Input:
            coco_anno_di= coordinate or relative coordinate Dictionary
            offset= ('pad_to_orig', 'orig_to_pad')
            rel_padding_ht_wd= (0.35, 0.35)
        Return:
            coco_anno_di (updated)
        '''
        new_anno_di = {}
        new_anno_di['info'] = coco_anno_di['info']
        new_anno_di['images'] = []
        new_anno_di['annotations'] = []
        new_anno_di['categories'] = coco_anno_di['categories']

        ## working on each image
        for ii in range(len(coco_anno_di['images'])):

            ## single coco annotation
            scdi = WholeCoco2SingleImgCoco(None, coco_anno_di).run(
                ii, index_type='general_index')

            ## adding padding info in coco "images" li
            t_di = scdi['images'][0]  # only a single dict in list
            # scdi['images'][0] = { ## causes other information if present to get loose
            #     'id': t_di['id'],
            #     'file_name': t_di['file_name'],
            #     'width': t_di['width'],
            #     'height': t_di['height'],
            #     'padx': int(rel_padding_ht_wd[1]*t_di['width']),
            #     'pady': int(rel_padding_ht_wd[0]*t_di['height']),
            #     'padded_width': int( t_di['width']*(1+2*rel_padding_ht_wd[1]) ),
            #     'padded_height': int( t_di['height']*(1+2*rel_padding_ht_wd[0]) )
            # }
            t_di['padx'] = int(rel_padding_ht_wd[1]*t_di['width']),
            t_di['pady'] = int(rel_padding_ht_wd[0]*t_di['height']),
            t_di['padded_width'] = int(t_di['width']*(1+2*rel_padding_ht_wd[1])),
            t_di['padded_height'] = int(t_di['height']*(1+2*rel_padding_ht_wd[0]))
            scdi['images'][0] = t_di

            ## modifying coordinate based on information change according to padding
            scdi['annotations'] = [
                self._offset_one_annotation(
                    anno_info,
                    offset=offset,
                    rel_padding_ht_wd=rel_padding_ht_wd
                )
                for anno_info in scdi['annotations']
            ]

            ## adding element back to main di
            new_anno_di['images'].extend(scdi['images'])
            new_anno_di['annotations'].extend(scdi['annotations'])

        ## return the processed di
        return new_anno_di

    ## -------------------------------------------------------< Related to Offset (End)

    ## -------------------------------------------------------< Related to Crop (Start)

    def _new_coord_after_crop(
        self, anno_li, rel_crop_pt1_pt2=((0.1,0.1), (0.9,0.9))
    ):
        '''
        Desc:
        '''
        (x1,y1), (x2,y2), = rel_crop_pt1_pt2
        x, y = (x2-x1), (y2-y1)
        return [
            (rel_coord-x1)/x if self._is_x_coord(i) else (rel_coord-y1)/y
            for i,rel_coord in enumerate(anno_li)
        ]

    def _crop_one_annotation(self, anno_info, rel_crop_pt1_pt2=((0.1,0.1), (0.9,0.9))):
        ''' works on a element '''
        o2p = self.convert_coord_from_orig_to_pad_addition

        if rel_crop_pt1_pt2 is not None:

            ## converting segmentation
            anno_info['segmentation'] = [
                self._new_coord_after_crop(anno, rel_crop_pt1_pt2)
                for anno in anno_info['segmentation']
            ]

            ## converting bbox
            anno_info['bbox'] = self._new_coord_after_crop(
                anno_info['bbox'], rel_crop_pt1_pt2)

        else:
            raise Exception('"rel_crop_pt1_pt2" is None')

        return anno_info

    def crop_annotation_based_on_rel_size(self, coco_rel_di, rel_crop_pt1_pt2=((0.1,0.1), (0.9,0.9))):
        '''
        Input:
            coco_rel_di= relative coordinate Dictionary
            pt1 == a == (x1,y1); pt2 == c == (x2,y2)
                _________________________
               |  a ___________ b        |
               |   |           |         |
               |   |           |         |
               |   |___________|         |
               |  d            c         |
               |_________________________|

        Return:
            coco_anno_di (updated)
        '''
        new_anno_di = {}
        new_anno_di['info'] = coco_rel_di['info']
        new_anno_di['images'] = []
        new_anno_di['annotations'] = []
        new_anno_di['categories'] = coco_rel_di['categories']

        ## working on each image
        for ii in range(len(coco_rel_di['images'])):

            ## single coco annotation
            scdi = WholeCoco2SingleImgCoco(None, coco_rel_di).run(
                ii, index_type='general_index')

            ## adding padding info in coco "images" li
            # t_di = scdi['images'][0]  # only a single dict in list
            # t_di['crop_pt1_pt2'] = rel_crop_pt1_pt2,
            # scdi['images'][0] = t_di

            li = []
            for d in scdi['images']:
                d['crop_pt1_pt2'] = rel_crop_pt1_pt2
                li.append(d)
            scdi['images'] = li

            ## modifying coordinate based on information change according to padding
            scdi['annotations'] = [
                self._crop_one_annotation(
                    anno_info,
                    rel_crop_pt1_pt2=rel_crop_pt1_pt2
                )
                for anno_info in scdi['annotations']
            ]

            ## adding element back to main di
            new_anno_di['images'].extend(scdi['images'])
            new_anno_di['annotations'].extend(scdi['annotations'])

        ## return the processed di
        return new_anno_di

    ## -------------------------------------------------------< Related to Crop (End)

    def run(self, coco_di, offset=None, rel_padding_ht_wd=None, rel_crop_pt1_pt2=None, inplace=False):
        '''
        Desc: If offset is None then just convert the annotation to Relative
        Input:
            coco_di
            offset:
                None (Just Perform Annotation conversion to relative)
                'orig_to_pad' (convert annotaion from Original based to padding)
                'pad_to_orig' (convert annotaion from padding based to original)
            rel_padding_ht_wd
                What paddign was used
            rel_crop_pt1_pt2=((0.1,0.1), (0.9,0.9))
        '''
        coco_ann_di = coco_di if inplace else deepcopy(coco_di)

        coco_rel_anno = self.gen_coco_rel_anno(coco_ann_di)

        ## related to padding
        if offset is not None:
            if rel_padding_ht_wd is None:
                raise Exception('Relative padding size can\'t be "None" when transforming b/c of padding')

            coco_rel_anno = self.offset_whole_coco_annotation(
                coco_rel_anno, offset=offset, rel_padding_ht_wd=rel_padding_ht_wd
            )

        ## related to cropping of annotation
        if rel_crop_pt1_pt2 is not None:
            coco_rel_anno = self.crop_annotation_based_on_rel_size(
                coco_rel_anno, rel_crop_pt1_pt2=rel_crop_pt1_pt2)

        return coco_rel_anno


''' ## Sample Code
coco_path= 'data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json'

## Reading Whole annotation from a path
whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)
print( whole_anno_di['annotations'][0]['bbox'] )

## (1) Convert Coco Annotation to Coco Relative Annotation: (1) inplace OFF
rel_coco_di = Coco2CocoRel().run(whole_anno_di)
print( rel_coco_di['annotations'][0]['bbox'] )

## (1) Convert Coco Annotation to Coco Relative Annotation: (2) inplace ON
Coco2CocoRel().run(whole_anno_di, inplace=True)
print( whole_anno_di['annotations'][0]['bbox'] )

## (2) Auto Detection of Coco Relative Annotation to NOT operate again
# "Data is already scaled to relative dimensions" - msg gets displayed but no exceeption
rel_coco_di = Coco2CocoRel().run(whole_anno_di)
print('\n AutoDetection: - Operations NOT Performed')
print( whole_anno_di['annotations'][0]['bbox'] )
print( rel_coco_di['annotations'][0]['bbox'] )

## (3) Effect of Padding Addition:
whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)
single_coco_di = WholeCoco2SingleImgCoco(coco_di=whole_anno_di).run(0)

print('Without Offset, Coco Annotation\n{}\n{}'.format(
    str(single_coco_di['images'][0]), str(single_coco_di['annotations'][0]['segmentation'])))

rel_coco_di = Coco2CocoRel().run(single_coco_di)
print('\n\nWithout Offset, Coco Relative Annotation\n{}\n{}'.format(
    str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

## (3) Offset the Abs Coordinate: (1) B/C padding(relative dim) was added
rel_coco_di = Coco2CocoRel().run(single_coco_di, offset='orig_to_pad', rel_padding_ht_wd=(0.5,0.5))
print('\n\nAbsolute Coord Offset: orig_to_pad\n{}\n{}'.format(
    str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

## (3) Offset the Abs Coordinate: (2) B/C added padding(relative dim) was removed
rel_coco_di = Coco2CocoRel().run(single_coco_di, offset='pad_to_orig', rel_padding_ht_wd=(0.5,0.5))
print('\n\nAbsolute Coord Offset: pad_to_orig\n{}\n{}'.format(
    str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))


## (4) Offset the relative coordinate
print('-'*100)
rel_coco_di = Coco2CocoRel().run(single_coco_di)
rel_coco_di = Coco2CocoRel().run(rel_coco_di, offset='pad_to_orig', rel_padding_ht_wd=(0.5,0.5))
print('\n\nRelative Coord Offset: \n{}\n{}'.format(
    str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

## (5) Cropping the annotation
print('-'*100)
whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)
rel_coco_di = Coco2CocoRel().run(single_coco_di)
print('\n\nRelative Coord Before Crop: \n{}\n{}'.format(
    str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

rel_coco_di = Coco2CocoRel().run(rel_coco_di, rel_crop_pt1_pt2=((0.25,0.25), (0.75,0.75)))

print('\n\nRelative Coord After Crop: \n{}\n{}'.format(
    str(rel_coco_di['images'][0]), str(rel_coco_di['annotations'][0]['segmentation'])))

# '''

'''
coco_path= 'data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json'
whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)
single_coco_di = WholeCoco2SingleImgCoco(coco_di=whole_anno_di).run(0)
rel_coco_di = Coco2CocoRel().run(single_coco_di)
print(rel_coco_di['annotations'][0]['bbox'])

## On Single
crop_rel_coco_di = Coco2CocoRel().run(whole_anno_di, rel_crop_pt1_pt2=((0.25,0.25), (0.75,0.75)))
print('\n',crop_rel_coco_di['annotations'][0]['bbox'])

## On Whole
crop_rel_coco_di = Coco2CocoRel().run(whole_anno_di, rel_crop_pt1_pt2=((0.25,0.25), (0.75,0.75)))
print('\n',crop_rel_coco_di['annotations'][0]['bbox'])
'''
