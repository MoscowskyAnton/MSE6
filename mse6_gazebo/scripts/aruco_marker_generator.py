#!/usr/bin/env python
# coding: utf-8

''' 
ArUco codes generator
'''

import cv2 
from cv2 import aruco
import argparse
import os
import rospy
import subprocess
import numpy as np
import re
import yaml

def read_food_types(food_types_file):
    with open(food_types_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def generate_aruco(aruco_id=None, path_to_textures=None, type=0):    

    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_1000)    
    print("generating {} marker...".format(aruco_id))
    IMG_SIZE=300
    BRD_SIZE=int(IMG_SIZE*0.05)
    img = aruco.drawMarker(aruco_dict, aruco_id, IMG_SIZE)
    img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)        
    
    i = img.copy()    
    i = cv2.copyMakeBorder(i, BRD_SIZE, BRD_SIZE, BRD_SIZE, BRD_SIZE, cv2.BORDER_CONSTANT, None, value=[255,255,255])
    file_name='Aruco{}.png'.format(aruco_id)
            
    
    path_to_file = os.path.join(path_to_textures, file_name)
    cv2.imwrite(path_to_file,i)        
    
    return file_name

def generate_material_files(path=None, a_file_name=None):    

    file_content=""
    
    file_name, file_extension = os.path.splitext(a_file_name)

    file_content+="material {}{{ \n \
        technique \n \
        {{ \n \
        pass \n \
        {{ \n \
            texture_unit \n \
            {{ \n \
            texture {} \n \
            scale 1 1 \n \
            }} \n \
        }}    \n \
        }} \n \
    }}\n\n".format(file_name, a_file_name)
    
     
    pattern = "(Aruco[\d]+)"
    fl = re.findall(pattern, file_name)[0]
    
    path_to_file = os.path.join(path_to_materials, fl+'.material')
    with open(path_to_file, 'w') as f:
        f.write(file_content)
        f.close()


if __name__ == "__main__":
    rospy.init_node('arUco generator')
    pkg_dir=rospy.get_param('~pkg_dir')    
    number = rospy.get_param('~number')
        
    path_to_textures = os.path.join(pkg_dir, 'media', 'materials', 'textures')
    
    if not os.path.isdir(path_to_textures):
        try:
            os.makedirs(path_to_textures)
        except OSError:
            rospy.logerr(f'Unable to create path {path_to_textures}!')
            exit()
    
    
    path_to_materials = os.path.join(pkg_dir, 'media', 'materials', 'scripts')
    if not os.path.isdir(path_to_materials):
        try:
            os.makedirs(path_to_materials)
        except OSError:
            rospy.logerr(f'Unable to create path {path_to_materials}!')
            exit()
    
    
    try:
        for aid in range(number):
            files = generate_aruco(aid, path_to_textures)
            generate_material_files(path_to_materials, files)
    except Exception as e:
        print(e)
        raise
    
    print("DONE!")
