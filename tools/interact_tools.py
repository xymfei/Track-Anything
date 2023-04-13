import time
import torch
import cv2
from PIL import Image, ImageDraw, ImageOps
import numpy as np
from typing import Union
from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator
import matplotlib.pyplot as plt
import PIL
from mask_painter import mask_painter as mask_painter2
from base_segmenter import BaseSegmenter
from painter import mask_painter, point_painter


mask_color = 3
mask_alpha = 0.7
contour_color = 1
contour_width = 5
point_color = 5
point_alpha = 0.9
point_radius = 15
contour_color = 2
contour_width = 5


def initialize():
    '''
    initialize sam controler
    '''
    SAM_checkpoint= '/ssd1/gaomingqi/checkpoints/sam_vit_h_4b8939.pth'
    model_type = 'vit_h'
    device = "cuda:0"
    sam_controler = BaseSegmenter(SAM_checkpoint, model_type, device)
    return sam_controler


def seg_again(sam_controler, image: np.ndarray):
    '''
    it is used when interact in video
    '''
    sam_controler.reset_image()
    sam_controler.set_image(image)
    return
    

def first_frame_click(sam_controler, image: np.ndarray, points:np.ndarray, labels: np.ndarray, multimask=True):
    '''
    it is used in first frame in video
    return: mask, logit, painted image(mask+point)
    '''
    sam_controler.set_image(image) 
    prompts = {
        'point_coords': points,
        'point_labels': labels,
    }
    masks, scores, logits = sam_controler.predict(prompts, 'point', multimask)
    mask, logit = masks[np.argmax(scores)], logits[np.argmax(scores), :, :]
    
    painted_image = mask_painter(image, mask.astype('uint8'), mask_color, mask_alpha, contour_color, contour_width)
    painted_image = point_painter(painted_image, points, point_color, point_alpha, point_radius, contour_color, contour_width)
    painted_image = Image.fromarray(painted_image)
    
    return mask, logit, painted_image

def interact_loop(sam_controler, image:np.ndarray, same: bool, points:np.ndarray, labels: np.ndarray, logits: np.ndarray=None, multimask=True):
    if same: 
        '''
        true; loop in the same image
        '''
        prompts = {
            'point_coords': points,
            'point_labels': labels,
            'mask_input': logits[None, :, :]
        }
        masks, scores, logits = sam_controler.predict(prompts, 'both', multimask)
        mask, logit = masks[np.argmax(scores)], logits[np.argmax(scores), :, :]
        
        painted_image = mask_painter(image, mask.astype('uint8'), mask_color, mask_alpha, contour_color, contour_width)
        painted_image = point_painter(painted_image, points, point_color, point_alpha, point_radius, contour_color, contour_width)
        painted_image = Image.fromarray(painted_image)

        return mask, logit, painted_image
    else:
        '''
        loop in the different image, interact in the video 
        '''
        if image is None:
            raise('Image error')
        else:
            seg_again(sam_controler, image)
        prompts = {
            'point_coords': points,
            'point_labels': labels,
        }
        masks, scores, logits = sam_controler.predict(prompts, 'point', multimask)
        mask, logit = masks[np.argmax(scores)], logits[np.argmax(scores), :, :]
        
        painted_image = mask_painter(image, mask.astype('uint8'), mask_color, mask_alpha, contour_color, contour_width)
        painted_image = point_painter(painted_image, points, point_color, point_alpha, point_radius, contour_color, contour_width)
        painted_image = Image.fromarray(painted_image)

        return mask, logit, painted_image
        
    


if __name__ == "__main__":
    points = np.array([[500, 375], [1125, 625]])
    labels = np.array([1, 1])
    image = cv2.imread('/hhd3/gaoshang/truck.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    sam_controler = initialize()
    mask, logit, painted_image_full = first_frame_click(sam_controler,image, points, labels, multimask=True)
    painted_image = mask_painter2(image, mask.astype('uint8'), background_alpha=0.8)
    painted_image = cv2.cvtColor(painted_image, cv2.COLOR_RGB2BGR)  # numpy array (h, w, 3)
    cv2.imwrite('/hhd3/gaoshang/truck_point.jpg', painted_image)
    painted_image_full.save('/hhd3/gaoshang/truck_point_full.jpg')
    
    mask, logit, painted_image_full = interact_loop(sam_controler,image,True, points, np.array([1, 0]), logit, multimask=True)
    painted_image = mask_painter2(image, mask.astype('uint8'), background_alpha=0.8)
    painted_image = cv2.cvtColor(painted_image, cv2.COLOR_RGB2BGR)  # numpy array (h, w, 3)
    cv2.imwrite('/hhd3/gaoshang/truck_same.jpg', painted_image)
    painted_image_full.save('/hhd3/gaoshang/truck_same_full.jpg')
    
    mask, logit, painted_image_full = interact_loop(sam_controler,image, False, points, labels, multimask=True)
    painted_image = mask_painter2(image, mask.astype('uint8'), background_alpha=0.8)
    painted_image = cv2.cvtColor(painted_image, cv2.COLOR_RGB2BGR)  # numpy array (h, w, 3)
    cv2.imwrite('/hhd3/gaoshang/truck_diff.jpg', painted_image)
    painted_image_full.save('/hhd3/gaoshang/truck_diff_full.jpg')
    
    
    
    
    
    
    


    
    
    