#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster

class OdomFromGazebo(Node):
    def __init__(self):
        super().__init__('odom_publisher')
        # Activer sim_time
        self.set_parameters([rclpy.parameter.Parameter(
            'use_sim_time', rclpy.Parameter.Type.BOOL, True)])
        
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.sub = self.create_subscription(
            PoseArray,
            '/model/hexapod_pkg/pose',
            self.pose_callback,
            10
        )
        self.get_logger().info('OdomFromGazebo started with sim_time!')

    def pose_callback(self, msg):
        if not msg.poses:
            return
        pose = msg.poses[0]
        # Utiliser le timestamp du message (sim time)
        now = msg.header.stamp if msg.header.stamp.sec > 0 else self.get_clock().now().to_msg()

        # TF odom → base_footprint
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = pose.position.x
        t.transform.translation.y = pose.position.y
        t.transform.translation.z = 0.0
        t.transform.rotation = pose.orientation
        self.tf_broadcaster.sendTransform(t)

        # Odometry
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = pose.position.x
        odom.pose.pose.position.y = pose.position.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation = pose.orientation
        self.odom_pub.publish(odom)

def main():
    rclpy.init()
    rclpy.spin(OdomFromGazebo())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
