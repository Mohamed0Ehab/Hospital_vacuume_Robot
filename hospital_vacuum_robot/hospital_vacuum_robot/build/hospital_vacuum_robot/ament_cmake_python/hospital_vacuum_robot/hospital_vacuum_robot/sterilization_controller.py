#!/usr/bin/env python3
"""
UV-C Sterilization Controller
==============================
Subscribes to /sterilize_on (Bool).
Publishes /sterilize_status (String) for logging/display.

Safety rules enforced:
  - UV-C ON only when robot velocity is ~0
  - Logs warning if someone tries to activate while moving
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
from geometry_msgs.msg import Twist


class SterilizationController(Node):
    def __init__(self):
        super().__init__('sterilization_controller')

        self.uvc_on        = False
        self.robot_moving  = False

        self.create_subscription(Bool,  '/sterilize_on', self._sterilize_cb, 10)
        self.create_subscription(Twist, '/cmd_vel',       self._cmd_vel_cb,  10)

        self.status_pub = self.create_publisher(String, '/sterilize_status', 10)
        self.create_timer(1.0, self._publish_status)

        self.get_logger().info('SterilizationController ready')

    def _cmd_vel_cb(self, msg: Twist):
        spd = abs(msg.linear.x) + abs(msg.angular.z)
        self.robot_moving = spd > 0.01

        # Safety: force UV off if robot starts moving
        if self.robot_moving and self.uvc_on:
            self.uvc_on = False
            self.get_logger().warn('⚠️  UV-C auto-disabled: robot is moving!')

    def _sterilize_cb(self, msg: Bool):
        if msg.data and self.robot_moving:
            self.get_logger().warn('🚫 Cannot activate UV-C while robot is moving!')
            return
        self.uvc_on = msg.data
        state = 'ON 🟣' if self.uvc_on else 'OFF ⚫'
        self.get_logger().info(f'UV-C sterilizer: {state}')

    def _publish_status(self):
        s = String()
        s.data = f"UV-C: {'ACTIVE' if self.uvc_on else 'INACTIVE'} | Moving: {self.robot_moving}"
        self.status_pub.publish(s)


def main(args=None):
    rclpy.init(args=args)
    node = SterilizationController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
