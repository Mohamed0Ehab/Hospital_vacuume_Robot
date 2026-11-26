#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
import math

class DiffDriveKinematics(Node):
    def __init__(self):
        super().__init__('diff_drive_kinematics')
        self.wheel_separation = 0.30
        self.wheel_radius     = 0.05
        self.x   = 0.0
        self.y   = 0.0
        self.yaw = 0.0
        self.v   = 0.0
        self.w   = 0.0
        self.last_time = self.get_clock().now()
        self.tf_broadcaster = TransformBroadcaster(self)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.create_timer(0.02, self.publish_tf)
        self.get_logger().info('DifferentialDriveKinematics node started ✓')

    def cmd_cb(self, msg):
        self.v = msg.linear.x
        self.w = msg.angular.z

    def publish_tf(self):
        now = self.get_clock().now()
        dt  = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now
        if dt <= 0.0 or dt > 1.0:
            return

        delta_s   = self.v * dt
        delta_yaw = self.w * dt
        self.x   += delta_s * math.cos(self.yaw + delta_yaw / 2.0)
        self.y   += delta_s * math.sin(self.yaw + delta_yaw / 2.0)
        self.yaw += delta_yaw

        stamp = now.to_msg()

        t = TransformStamped()
        t.header.stamp    = stamp
        t.header.frame_id = 'odom'
        t.child_frame_id  = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        cy = math.cos(self.yaw / 2.0)
        sy = math.sin(self.yaw / 2.0)
        t.transform.rotation.z = sy
        t.transform.rotation.w = cy
        self.tf_broadcaster.sendTransform(t)

        odom = Odometry()
        odom.header.stamp    = stamp
        odom.header.frame_id = 'odom'
        odom.child_frame_id  = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = sy
        odom.pose.pose.orientation.w = cy
        odom.twist.twist.linear.x  = self.v
        odom.twist.twist.angular.z = self.w
        self.odom_pub.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveKinematics()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
