
from copy import deepcopy


class AggreagateCoco:

    def __init__(self, *annotation_li):
        '''
        Input:
            either pass multiple coco dictionary as args or list of such dicts
        '''
        annotation_li = deepcopy(annotation_li)
        templili = [[e] if isinstance(e,dict) else e for e in annotation_li]
        self.annotation_li = [ee for e in templili for ee in e]

    def get_coco_value_categories(self):
        '''
        Returns:
            cat_coco_li: value 
        '''
        catalogged_cat_li = []
        for i,idi in enumerate(self.annotation_li):
            for iidi in idi['categories']:
                cat_name = iidi['name']
                if cat_name not in catalogged_cat_li:
                    catalogged_cat_li.append(cat_name)

        cat_rev_di = {e:(i+1) for i,e in enumerate(catalogged_cat_li)}
        # { item:k for k,item in all_cat_di.items() }

        cat_coco_li = [{'id': i+1, 'name': e} for i,e in enumerate(catalogged_cat_li)]

        return cat_coco_li, cat_rev_di

    def _generate_suffix(self, file_name):
        # file_name = 'Something ({0:03.0f})'.format(9)
        sel = file_name.split(' ')[-1][1:-1]
        if len(sel)==3 and sel.isdigit():
            suffix = ' ({0:03.0f})',format(int(sel)+1)
        else:
            suffix = ' (001)'
        return file_name

    def generate_imgs_and_annotations_li(
        self, all_category_map_di, if_img_name_match='skip', show_warning=True
    ):
        '''
        options:
            all_category_map_di = {
                'coffee-bean': 1,
                'tea-seed': 2,
                'mango': 3,
                'lemon': 4,
                'orange': 5
            }
            if_img_name_match='skip', 'append'
        '''
        ## coco annotation in annotation_li will be rotated index-wise, sort and append that pair to main accordingly
        all_images_li, all_annotations_li = [], []
        all_category_map_di = deepcopy(all_category_map_di)
        img_map_di = {}

        for i,idi in enumerate(self.annotation_li):

            ## info in these ann
            ann_img_li, ann_anno_li = self.annotation_li[i]['images'], self.annotation_li[i]['annotations']
            ann_cat_map_di = {di['id']:di['name'] for di in self.annotation_li[i]['categories']}

            ## working on images
            int_img_map_di = {imdi['id']:imdi['file_name'] for imdi in ann_img_li}

            ## individual image_di
            for imdi in ann_img_li:
                file_name = imdi['file_name']
                if file_name in img_map_di:
                    if show_warning:
                        print(f'There\'s already a record present for the image with name "{file_name}".')
                    if if_img_name_match=='append':
                        file_name = file_name+self._generate_suffix(file_name)
                        ## mapping dict
                        img_map_di[file_name] = len(img_map_di)
                    elif if_img_name_match=='skip':
                        continue  # skip this file
                else:
                    ## mapping dict
                    img_map_di[file_name] = len(img_map_di)

                ## appending to main
                imdi['id'] = img_map_di[file_name]
                imdi['file_name'] = file_name
                all_images_li.append(imdi)

            ## individual annotation
            for andi in ann_anno_li:
                anid, animid = andi['id'], andi['image_id']
                an_cat_name = ann_cat_map_di[andi['category_id']]
                fn_int_di = int_img_map_di[animid]

                ## overwriting some information
                andi['id'] = len(all_annotations_li)
                andi['image_id'] = img_map_di[fn_int_di]
                andi['category_id'] = all_category_map_di[an_cat_name]
                all_annotations_li.append(andi)

        return all_images_li, all_annotations_li

    def run(self, if_img_name_match='skip', show_warning=True):
        '''
            if_img_name_match='skip', 'append'
            show_warning: boolean
        '''
        agg_coco_di = {}
        agg_coco_di['info'] = {'description': 'agg-coco-data'}
        agg_coco_di['categories'], all_cat_rev_di = self.get_coco_value_categories()
        agg_coco_di['images'], agg_coco_di['annotations'] = self.generate_imgs_and_annotations_li(
            all_cat_rev_di, if_img_name_match=if_img_name_match, show_warning=show_warning)

        return agg_coco_di


'''
agg_coco_di = AggreagateCoco(annotation_li).run(if_img_name_match='skip')
# agg_coco_di = AggreagateCoco(annotation_li).run(if_img_name_match='append')

print('#images :', len(agg_coco_di['images']))
print('#annotation :', len(agg_coco_di['annotations']))

'''
