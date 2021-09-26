#!/usr/bin/env python

import rospy
from gazebo_msgs.msg import ModelStates

import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import PoseStamped, TransformStamped

class GazeboGroundTruthLocalizer(object):
    
    def __init__(self):
        rospy.init_node('gazebo_ground_truth_localizer')
        
        #self.rate_hz = rospy.get_param('~rate_hz', 10)
        self.robot_name = rospy.get_param('~robot_name', 'mse6')
        self.robot_frame = rospy.get_param('~robot_frame', 'base_link')
        self.odom_frame = rospy.get_param('~odom_frame', 'odom')
        
        self.tf_buffer = tf2_ros.Buffer(rospy.Duration(1200.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()
        
        rospy.Subscriber('/gazebo/model_states', ModelStates, self.model_states_cb)
        
    def model_states_cb(self, msg):
        for i, name in enumerate(msg.name):
            if name == self.robot_name:
                
                try:
                    transform = self.tf_buffer.lookup_transform(self.odom_frame,
                                       self.robot_frame, #source frame
                                       rospy.Time(0), #get the tf at first available time
                                       rospy.Duration(0.1)) #wait for 0.1 second
                
                except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
                    break
                
                robot_pose_global = PoseStamped()
                robot_pose_global.pose = msg.pose[i]
                robot_pose_global.header.frame_id = 'map'
                robot_pose_global.header.stamp = rospy.Time.now()
                
                odom_pose_global = tf2_geometry_msgs.do_transform_pose(robot_pose_global, transform)
                
                transform_map_odom = TransformStamped()
                
                transform_map_odom.header = robot_pose_global.header
                transform_map_odom.child_frame_id = self.odom_frame
                
                transform_map_odom.transform.translation.x = odom_pose_global.pose.position.x
                transform_map_odom.transform.translation.y = odom_pose_global.pose.position.y
                transform_map_odom.transform.translation.z = odom_pose_global.pose.position.z
                
                transform_map_odom.transform.rotation = odom_pose_global.pose.orientation
                
                self.tf_broadcaster.sendTransform(transform_map_odom)
                
                break
                
                
    def run(self):
        rospy.spin()
        
        
if __name__ == '__main__':
    ggtl = GazeboGroundTruthLocalizer()
    ggtl.run()
        
        
        
