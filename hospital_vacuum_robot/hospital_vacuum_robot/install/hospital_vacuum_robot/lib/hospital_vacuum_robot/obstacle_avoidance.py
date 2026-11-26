#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math


class ObstacleAvoidance(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance')
        self.safe_distance   = 1.0
        self.danger_distance = 0.6
        self.linear_speed    = 0.25
        self.turn_speed      = 0.7
        self.create_subscription(LaserScan, '/scan', self._scan_cb, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Obstacle avoidance node started ✓')

    def _get_min(self, ranges, start_deg, end_deg):
        total = len(ranges)
        def safe(r):
            return r if (not math.isnan(r) and not math.isinf(r) and r > 0.05) else 999.0
        start = int((start_deg / 360.0) * total)
        end   = int((end_deg   / 360.0) * total)
        if start <= end:
            vals = [safe(ranges[i]) for i in range(start, end)]
        else:
            vals = [safe(ranges[i]) for i in range(start, total)] + \
                   [safe(ranges[i]) for i in range(0, end)]
        return min(vals) if vals else 999.0

    def _scan_cb(self, msg):
        r = msg.ranges
        front       = self._get_min(r, 340, 20)
        front_left  = self._get_min(r, 20,  80)
        front_right = self._get_min(r, 280, 340)
        left        = self._get_min(r, 80,  150)
        right       = self._get_min(r, 210, 280)

        cmd = Twist()

        if front < self.danger_distance:
            cmd.linear.x = -0.1
            cmd.angular.z = self.turn_speed if left > right else -self.turn_speed

        elif front < self.safe_distance:
            cmd.linear.x  = self.linear_speed * 0.4
            cmd.angular.z = self.turn_speed * 0.8 if left > right else -self.turn_speed * 0.8

        elif front_left < self.danger_distance:
            cmd.linear.x  = self.linear_speed * 0.7
            cmd.angular.z = -self.turn_speed * 0.6

        elif front_right < self.danger_distance:
            cmd.linear.x  = self.linear_speed * 0.7
            cmd.angular.z =  self.turn_speed * 0.6

        elif front_left < self.safe_distance:
            cmd.linear.x  = self.linear_speed
            cmd.angular.z = -self.turn_speed * 0.3

        elif front_right < self.safe_distance:
            cmd.linear.x  = self.linear_speed
            cmd.angular.z =  self.turn_speed * 0.3

        else:
            cmd.linear.x  = self.linear_speed
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)

        status = "FWD" if cmd.linear.x > 0 and cmd.angular.z == 0 else \
                 "TURN L" if cmd.angular.z > 0 else \
                 "TURN R" if cmd.angular.z < 0 else "BACK"

        self.get_logger().info(
            f'[{status}] F:{front:.2f} FL:{front_left:.2f} FR:{front_right:.2f} '
            f'L:{left:.2f} R:{right:.2f} | v={cmd.linear.x:.2f} w={cmd.angular.z:.2f}',
            throttle_duration_sec=0.5
        )


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
