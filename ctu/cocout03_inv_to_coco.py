
from copy import deepcopy


class CocoRel2CocoSpecificSize:
    
    ## convert coordinate to relative values
    def _is_x_coord(self, index):
        return index%2==0

    def _gen_abs_coordinate_li(self, rel_coord_li, img_width, img_height):
        ''' 
        rel_coord_li: [0.7349377026796378, 0.3037492177277122, 0.021164021164021187, 0.30357854013767976]
        to abs
        : [3386.5929339477707, 1049.7572964669732, 97.52380952380963, 1049.1674347158212]
        '''
        # sum([ e>1 for e in rel_coord_li ]) Disabling this warning
        # 
        # if (len(rel_coord_li)>1) and (max(rel_coord_li)>1):
        #     raise Exception('Data is already in absolute dimensions.'
        #                      ' Please Generate the Coco Relative Annotation.')
        #     return rel_coord_li
        return [ 
            coordinate*img_width if self._is_x_coord(i) else coordinate*img_height 
            for i,coordinate in enumerate(rel_coord_li) 
        ]
    
    def _transform_one_annotation(self, anno_info, desired_ht_wd):
        ''' works on a element ''' 
        img_ht, img_wd = desired_ht_wd
        anno_info['segmentation'] = [ self._gen_abs_coordinate_li(anno, img_wd, img_ht) 
                                     for anno in anno_info['segmentation'] ]
        anno_info['bbox'] = self._gen_abs_coordinate_li(anno_info['bbox'], img_wd, img_ht) 

        ## Delete area key if present
        anno_info.pop('area', None)
        return anno_info

    def run(self, rel_coco_di, desired_ht_wd=(1000,1000)):
        '''
        Input:
            rel_coco_di: coco_di in relative coordinate
            desired_ht_wd: change the coordinate according to the method
        Return:
            coco_di (in coordinate)
        '''
        new_di = deepcopy(rel_coco_di)

        for i,k in enumerate(new_di['annotations']):
            anno_info = new_di['annotations'][i]
            new_di['annotations'][i] = self._transform_one_annotation(anno_info, desired_ht_wd)

        return new_di

'''
## Getting COCO & COCO Relative annotation
coco_path= 'data/input/Annotations/coco-labels_wt-estimation-carrot-orange-potato.json'
whole_anno_di = WholeCoco2SingleImgCoco.read_annotation(coco_path)
single_coco_di = WholeCoco2SingleImgCoco(coco_di=whole_anno_di).run(0)
rel_coco_di = Coco2CocoRel().run(single_coco_di)

## Msg
print('\nCOCO Annotation:\n', single_coco_di['annotations'][0]['segmentation'])
print('\nCOCO Relative Annotation:\n', rel_coco_di['annotations'][0]['segmentation'])

## Convert it back to Absoulte Coordinate System for any image size: (1) From Coco Relative
new_coco_di = CocoRel2CocoSpecificSize().run(rel_coco_di, desired_ht_wd=(100,100))
print('\nNew COCO Relative Annotation for (100,100):\n', new_coco_di['annotations'][0]['segmentation'])

## Convert it back to Absoulte Coordinate System for any image size: (2) From Coco
# --> Error gets Generated
new_coco_di = CocoRel2CocoSpecificSize().run(single_coco_di, desired_ht_wd=(100,100))
# '''

