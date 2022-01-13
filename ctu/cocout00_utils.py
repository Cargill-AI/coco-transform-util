
import cv2
import numpy as np
import matplotlib.pyplot as plt


class ImgTransform:
    '''
    Some Basic Image Transformation utilities
    '''

    @staticmethod
    def resize_with_aspect_ratio(frame, width=None, height=None, inter=cv2.INTER_AREA):
        '''
        Desc: Resize the Image while maintaining the aspect ratio of it
              cv2.resize(image, (0, 0), None, .25, .25)
        Input:
            image
            width: final desired width,
                   if wd and ht both are NOT None; width is given a higher priority.
            height: final desired height
        Output:
            Return Image
        '''
        dim = None
        (h, w) = frame.shape[:2]

        if width is None and height is None:
            return frame
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(frame, dim, interpolation=inter)

    @staticmethod
    def add_relative_padding_to_image(img, rel_padding_ht_wd=(0.15,0.15), pad_color=(10,10,10)):
        '''
        Desc: Image will be kept at the center and equivalent size of padding will be
              added on two sides
              Add padding of pad_x*im_x_size on each side(x dir) of the image.

             +---------------------+  -
             |                     |  |  pad_y
             |   a ----------- b   |  -
             |    |           |    |
             |    |           |    |
             |   d ----------- c   |  -
             |                     |  |  pad_y
             +---------------------+  -
             |----|           |----|
              pad_x            pad_x

        Input:
            image
            rel_padding_ht_wd: a tuple containing the padding in x & y direction
            pad_color: padding color
        Output:
            Returns New Frame
        '''
        scht, scwd = img.shape[:2]
        extra_x, extra_y = int(scht*rel_padding_ht_wd[0]), int(scwd*rel_padding_ht_wd[1])
        top, bottom = extra_x, extra_x
        left, right = extra_y, extra_y

        pdd_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, 
                                     value=pad_color)
        return pdd_img

    @staticmethod
    def relative_size_based_crop(img, rel_pt1=None, rel_pt2=None):
        '''
        Desc:
            pt1 == a == (x1,y1); pt2 == c == (x2,y2)
                a ___________ b
                 |           |
                 |           |
                 |___________|
                d            c
        Input:
            image: Input Frame
            rel_pt1: PtA as shown above
                     Eg. None, (0.1,0.1) # None Means (0.0,0.0)
            rel_pt2: PtC as shown above
                     Eg. None, (0.9,0.9) # None Means (1.0,1.0)
        Output:
            Return Image
        '''
        ## Default Value
        if rel_pt1 is None: rel_pt1=(0.0,0.0)
        if rel_pt2 is None: rel_pt1=(1.0,1.0)

        (x1,y1),(x2,y2) = rel_pt1, rel_pt2
        ht,wd,_ = img.shape
        (x1,y1) = (int(wd*x1), int(ht*y1))
        (x2,y2) = (int(wd*x2), int(ht*y2))
        return img[y1:y2, x1:x2]


# -------------------------------------------------------------------------------------------------------- #

class BBox:
    '''
    Bounding Box is an enclosing retangular box for a image marking
    '''
    _c_polygons = None

    ## Value types of :class:`BBox`
    INSTANCE_TYPES = (np.ndarray, list, tuple)
    ## Bounding box format style [x1, y1, x2, y2]
    STYLE_MIN_MAX = 'minmax'
    ## Bounding box format style [x1, y1, width, height]
    STYLE_WIDTH_HEIGHT = 'widthheight'

    def __init__(self, bbox, style=None):
        '''
        Input:
            bbox: a array or list of length 4 or class (np.ndarray, list, tuple)
            style:
                option: 'minmax' format style [x1, y1, x2, y2]
                option: 'widthheight' format style [x1, y1, width, height]
        '''
        assert len(bbox) == 4
        self.style = style if style else BBox.STYLE_MIN_MAX  # None == False

        self._xmin = int(bbox[0])
        self._ymin = int(bbox[1])
        if self.style == self.STYLE_MIN_MAX:
            self._xmax = int(bbox[2])
            self._ymax = int(bbox[3])
            self.width = self._xmax - self._xmin
            self.height = self._ymax - self._ymin
        if self.style == self.STYLE_WIDTH_HEIGHT:
            self.width = int(bbox[2])
            self.height = int(bbox[3])
            self._xmax = self._xmin + self.width
            self._ymax = self._ymin + self.height

    @property
    def min_point(self):
        ''' Minimum points of the bounding box (x1, y1) '''
        return self._xmin, self._ymin

    @property
    def max_point(self):
        ''' Maximum points of the bounding box (x2, y2) '''
        return self._xmax, self._ymax

    def draw(self, image, color=None, thickness=2):
        '''
        Desc: Draws a bounding box to the image array of shape (width, height, 3)
              *This function modifies the image array*
        Input:
            color: RGB color repersentation (tuple, list)
            thickness: pixel thickness of box (int)
        '''
        if color is None: color = Visualize()._random_rgb_color()
        image_copy = image.copy()
        cv2.rectangle(image_copy, self.min_point, self.max_point, color=color, thickness=thickness)
        return image_copy


class Polygons:

    _c_bbox = None
    _c_mask = None

    _c_points = None
    _c_segmentation = None

    #: Polygon instance types
    INSTANCE_TYPES = (list, tuple)

    def __init__(self, polygons):
        self.polygons = [np.array(polygon).flatten() for polygon in polygons]

    @property
    def style_points(self):
        '''
        Returns polygon in point format:
            [
                [[x1, y1], [x2, y2], [x3, y3], ...],
                [[x1, y1], [x2, y2], [x3, y3], ...],
                ...
            ]
        '''
        if not self._c_points:
            self._c_points = [
                np.array(point).reshape(-1, 2).round().astype(int)
                for point in self.polygons ]
        return self._c_points

    @property
    def style_segmentation(self):
        '''
        Returns polygon in segmentation format:
            [
                [x1, y1, x2, y2, x3, y3, ...],
                [x1, y1, x2, y2, x3, y3, ...],
                ...
            ]
        '''
        if not self._c_segmentation:
            self._c_segmentation = [polygon.tolist() for polygon in self.polygons]
        return self._c_segmentation

    @classmethod
    def create(cls, polygons):
        if isinstance(polygons, Polygons.INSTANCE_TYPES):
            return Polygons(polygons)
        if isinstance(polygons, Polygons):
            return polygons
        return None

    def proj_to_bbox(self):
        '''
        Desc: Returns or generates `BBox` class representation of polygons.
        Return:
            `BBox` class repersentation
        '''
        if not self._c_bbox:

            y_min = x_min = float('inf')
            y_max = x_max = float('-inf')

            for point_list in self.style_points:
                minx, miny = np.min(point_list, axis=0)
                maxx, maxy = np.max(point_list, axis=0)

                y_min = min(miny, y_min)
                x_min = min(minx, x_min)
                y_max = max(maxy, y_max)
                x_max = max(maxx, x_max)

            self._c_bbox = BBox((x_min, y_min, x_max, y_max))
            self._c_bbox._c_polygons = self

        return self._c_bbox

    def proj_to_mask(self, width=None, height=None):
        '''
        Desc: Returns or generates `Mask` class representation of polygons.
        Retun:
            `Mask` class repersentation
        '''
        if not self._c_mask:
            # <todo code changes>
            # print((height, width))
            # if height is None and width is None: raise Exception('Mask Height and Width is Not Known')
            # print('-----||', (height, width))
            size = (height, width) if (height and width) else self.proj_to_bbox().max_point
            # Generate mask from polygons
            mask = np.zeros(size)
            mask = cv2.fillPoly(mask, self.style_points, 1)
            self._c_mask = Mask(mask)
            self._c_mask._c_polygons = self
        return self._c_mask

    def draw(self, image, color=None, thickness=3):
        '''
        Desc: Draws the polygons to the image array of shape (width, height, 3)
              *This function modifies the image array*
        Inputs:
            color: RGB color repersentation (type: tuple, list)
            thickness: pixel thickness of box (type: int)
        '''
        if color is None: 
            color = Visualize()._random_rgb_color()
        image_copy = image.copy()
        cv2.polylines(image_copy, self.style_points, isClosed=True, color=color, thickness=thickness)
        return image_copy


class Mask:
    ''' Mask class '''
    _c_polygons = None

    INSTANCE_TYPES = (np.ndarray,)

    def __init__(self, array):
        self.array = np.array(array, dtype=bool)

    def area_of_mask(self):
        return self.array.sum()

    def draw(self, image, color=None, alpha=0.5): 
        '''
        Draws current mask to the image array of shape (width, height, 3)

        This function modifies the image array
        Inputs:
            color: RGB color repersentation
                   type color: tuple, list
            alpha: opacity of mask
                   type alpha: float
        '''
        if color is None: color = Visualize()._random_rgb_color()
        image_copy = image.copy()
        for c in range(3):
            image_copy[:, :, c] = np.where(
                self.array,
                image_copy[:, :, c] * (1 - alpha) + alpha * color[c],
                image_copy[:, :, c]
            )
        return image_copy


# -------------------------------------------------------------------------------------------------------- #

class ColorRandom:
    @property
    def _rgb(self):
        color = list(np.random.choice(range(256), size=3))
        # color = np.random.randint(0, 255, size=(3, ))

        #convert data types int64 to int and return
        return (int(color[0]), int(color[1]), int(color[2])) 


class Visualize:
    '''
    '''

    def _view_img_using_matplot(self, image, title=None, figure_size=(6, 3)):
        ''' matplot based image view '''
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        fig = plt.figure(figsize=figure_size, dpi=150)# no visible frame
        if title is not None: plt.title(title)
        plt.imshow(img)
        plt.show()

    @staticmethod
    def draw_annotation(img, coco_ann_di=None, cls_mapper_di=None, 
                        draw_what=['bbox', 'polyline', 'mask'], thickness=10):
        '''
        Desc: Draw the annotation on Image

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
                    color = ColorRandom()._rgb
                else:
                    cls = str(ann['category_id'])
                    color = ColorRandom()._rgb

                    ## if already assigned then pick that color
                    if cls in color_di.keys():
                        color = color_di[cls]
                    else:
                        color_di[cls] = color

                ## draw what ever is asked
                pol = Polygons.create(ann['segmentation'])
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
        Visualize()._view_img_using_matplot(draw_im)

'''
img = cv2.imread('example_data/Coffee-beans.jpeg')
img = Transform.resize_with_aspect_ratio(img, width=300, height=900)
Visualize().draw_annotation(img)
'''


def create_mask(image, poly, transparent_mask=True):
    '''
    a mask is the same size as our image, but has only two pixel
    values, 0 and 255 -- pixels with a value of 0 (background) are
    ignored in the original image while mask pixels with a value of
    255 (foreground) are allowed to be kept
    Inputs:
        img: bgr image
        poly: anno['annotations'][0]['segmentation']; in segmentation format
            poly = [[300.63, 194.93, 324.29, 189.40, 340.06, 189.40, 350.44, 189.40, 
                     392.36, 218.17, 399.41, 247.32, 371.61, 285.32, 295.65, 285.69, 
                     271.58, 267.24, 266.18, 232.56, 287.35, 201.20]]
        transparent_mask: If False Boolean mask else transparent mask
    '''
    ## creating blank mask
    mask = np.zeros(image.shape[:2], dtype='uint8')

    ## marking poly-area in mask
    poly_pt_format = Polygons(poly).style_points
    cv2.fillPoly(mask, poly_pt_format, color=255)

    ## creating transparent mask if asked
    if transparent_mask:
        mask = cv2.bitwise_and(image, image, mask=mask)

    return mask


'''
mask = create_mask(image, poly, transparent_mask=True)
aml.viewImage(mask)
'''
