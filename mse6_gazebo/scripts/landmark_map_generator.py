#!/usr/bin/env python
# coding: utf-8
import rospy
import numpy as np
import subprocess
import yaml

class LandmarkMapGenerator():
        
        def __init__(self):
            
            rospy.init_node('landmark_map_generator')
            
            self.X = rospy.get_param('~X', 4)
            self.Y = rospy.get_param('~Y', 4)
            self.dX = rospy.get_param('~dX', 3)
            self.dY = rospy.get_param('~dY', 3)
            self.len = rospy.get_param('~len', 0.5)
                
            self.x = np.linspace(-self.X/2 * self.dX, self.X/2 * self.dX, self.X)
            self.y = np.linspace(-self.Y/2 * self.dY, self.Y/2 * self.dY, self.Y)
            
            self.mx, self.my = np.meshgrid(self.x, self.y)
            
            self.map_path = rospy.get_param("~map_path",'/tmp/map.yaml')
            self.map_dict = {}

        def run(self):
            counter = 0
            for i in range(self.mx.shape[0]):
                for j in range(self.my.shape[0]):                    
                    subprocess.Popen(['roslaunch', 'mse6_gazebo', 'spawn_landmark.launch', f'aruco_id:={counter}', f'x:={self.mx[i,j]}', f'y:={self.my[i,j]}', f'z:={0.5}', f'len:={self.len}'])
                    counter+=1
                    self.map_dict[counter] = {'x': float(self.mx[i,j]), 'y': float(self.my[i,j])}
                    
            stream = open(self.map_path, 'w')
            yaml.dump(self.map_dict, stream)
            
            
            
if __name__ == '__main__':
    lmg = LandmarkMapGenerator()
    lmg.run()
