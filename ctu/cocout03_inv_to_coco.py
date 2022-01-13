
from copy import deepcopy
from ctu.cocout00_utils import Polygons

class CocoRel2CocoSpecificSize:
    '''relative to coordinate system'''

    ## area calculation
    def _anno_area(self, img_ht_wd, segmentation=None, bbox=None):
        '''
        Adding Area
        if both segmentation and bbox is provided then segmentation is given higher priority.
        '''
        if segmentation is not None: 
            polygon = segmentation
        elif bbox is not None:
            x1, x2, y1, y2 = [bbox[0], bbox[0]+bbox[2], bbox[1], bbox[1]+bbox[3]] 
            polygon = [[x1, y1, x1, y2, x2, y2, x2, y1]] 
        else:
            raise Exception('Not Possible to calculate')

        pol = Polygons.create(polygon)
        mask = pol.proj_to_mask(width=img_ht_wd[1], height=img_ht_wd[0])
        return mask.area_of_mask()

    ## convert coordinate to relative values
    def _is_x_coord(self, index):
        return index%2==0
    
    def _transform_one_image_info(self, image_info, desired_ht_wd):
        ''' works on a element ''' 
        image_info['height'], image_info['width'] = desired_ht_wd
        return image_info

    def _crop_coord(self, ele, index, img_wd, img_ht):
        if self._is_x_coord(index):
            if ele < 0:
                return 0.0
            elif ele > img_wd:
                return float(img_wd)
            else:
                return ele
        else:
            if ele < 0:
                return 0.0
            elif ele > img_ht:
                return float(img_ht)
            else:
                return ele
    
    def _gen_abs_coordinate_li(self, rel_coord_li, img_wd, img_ht, crop_out_of_frame):
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
        if crop_out_of_frame:
            temp_li = [ 
                coordinate*img_wd if self._is_x_coord(i) else coordinate*img_ht 
                for i,coordinate in enumerate(rel_coord_li) 
            ]
            return [ self._crop_coord(e, i, img_wd, img_ht) for i,e in enumerate(temp_li) ]
        else:
            return [ 
                coordinate*img_wd if self._is_x_coord(i) else coordinate*img_ht 
                for i,coordinate in enumerate(rel_coord_li) 
            ]

    def _transform_one_annotation(self, anno_info, desired_ht_wd, crop_out_of_frame):
        ''' works on a element ''' 
        img_ht, img_wd = desired_ht_wd
        
        anno_info['segmentation'] = [ self._gen_abs_coordinate_li(anno, img_wd, img_ht, crop_out_of_frame) 
                for anno in anno_info['segmentation'] ]
        anno_info['bbox'] = self._gen_abs_coordinate_li(anno_info['bbox'], img_wd, img_ht, crop_out_of_frame) 

        ## calculated field
        anno_info['area'] = self._anno_area(desired_ht_wd, anno_info['segmentation'], anno_info['bbox'])
        anno_info['area'] = abs(int(anno_info['area'])) ## to make it json serializable
        ## Delete area key if present
        # anno_info.pop('area', None)

        return anno_info

    def run(self, rel_coco_di, desired_ht_wd=(1000,1000), crop_oof=True, area_thresh_for_oof=0):
        '''
        oof = out_of_frame
        
        Input:
            rel_coco_di: coco_di in relative coordinate
            desired_ht_wd: change the coordinate according to the method
            
            
        Return:
            coco_di (in coordinate)
        '''
        new_di = deepcopy(rel_coco_di)

        for i,k in enumerate(new_di['annotations']):
            
            ## anno_info
            anno_info = new_di['annotations'][i]
            new_di['annotations'][i] = self._transform_one_annotation(anno_info, desired_ht_wd, crop_oof)
            
            ## image_info
            image_index = [ i for i,e in enumerate(new_di['images']) 
               if e['id']==anno_info['image_id'] ][0]
            image_info = new_di['images'][image_index]
            new_di['images'][image_index] = self._transform_one_image_info(
                image_info, desired_ht_wd)
    
        ## remove those annotation with area 0 or less
        new_di['annotations'] = [ k for i,k in enumerate(new_di['annotations']) if k['area']>=float(area_thresh_for_oof) ]

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

