#!/usr/bin/env python

import rospy
from gazebo_msgs.msg import ModelStates

import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import PoseStamped, TransformStamped, Quaternion
import tf
import numpy as np
from gazebo_msgs.srv import GetModelState

class GazeboGroundTruthLocalizer(object):
    
    def __init__(self):
        rospy.init_node('gazebo_ground_truth_localizer')
        
        self.rate_hz = rospy.get_param('~rate_hz', 10)
        self.robot_name = rospy.get_param('~robot_name', 'mse6')
        self.robot_frame = rospy.get_param('~robot_frame', 'base_link')
        self.odom_frame = rospy.get_param('~odom_frame', 'odom')
        
        #self.
        
        self.tf_buffer = tf2_ros.Buffer(rospy.Duration(1200.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()                                
        
        rospy.wait_for_service('/gazebo/get_model_state')
        self.get_model_state_srv = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
                        
        rospy.Timer(rospy.Duration(1./self.rate_hz), self.timer_cb)
        
    def timer_cb(self, event):        
        model_state = self.get_model_state_srv(self.robot_name,"")
        
        if model_state.success:        
            try:
                odom_bl_tf = self.tf_buffer.lookup_transform(self.odom_frame,
                                    self.robot_frame, #source frame
                                    rospy.Time(0), #get the tf at first available time
                                    rospy.Duration(0.1)) #wait for 0.1 second
            
            except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
                rospy.logerr(f"Timed out transform from {self.odom_frame} to {self.robot_frame}")
                return
            
            odom_bl_mat = tf.transformations.compose_matrix(
                translate = [odom_bl_tf.transform.translation.x,
                        odom_bl_tf.transform.translation.y,
                        odom_bl_tf.transform.translation.z],
                angles = euler_from_quaternion_msg(odom_bl_tf.transform.rotation))                                            
                
            map_bl_mat = tf.transformations.compose_matrix(
                translate = [model_state.pose.position.x, model_state.pose.position.y, model_state.pose.position.z],
                angles = euler_from_quaternion_msg(model_state.pose.orientation))
            
            map_odom_mat = np.dot(map_bl_mat, np.linalg.inv(odom_bl_mat) )
    
            _, _, angles, trans, _ = tf.transformations.decompose_matrix(map_odom_mat)
            
            tfs = TransformStamped()
    
            tfs.header.stamp = model_state.header.stamp + rospy.Duration(0.015)
            tfs.header.frame_id = 'map'
            tfs.child_frame_id = self.odom_frame
            tfs.transform.translation.x = trans[0]
            tfs.transform.translation.y = trans[1]
            tfs.transform.translation.z = trans[2]
            tfs.transform.rotation = quaternion_msg_from_euler(angles)
            
            self.tf_broadcaster.sendTransform(tfs)                                
                
    def run(self):
        rospy.spin()
        
        
def euler_from_quaternion_msg(q_msg):
    qu = []
    qu.append(q_msg.x)
    qu.append(q_msg.y)
    qu.append(q_msg.z)
    qu.append(q_msg.w)

    return tf.transformations.euler_from_quaternion(qu)   

def quaternion_msg_from_euler(euler):
    qu = tf.transformations.quaternion_from_euler(euler[0],euler[1],euler[2])    
    msg = Quaternion()
    msg.x = qu[0]
    msg.y = qu[1]
    msg.z = qu[2]
    msg.w = qu[3]
    return msg

if __name__ == '__main__':
    ggtl = GazeboGroundTruthLocalizer()
    ggtl.run()
        
        
        
