#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class AutoExplorer(Node):
    def __init__(self):
        super().__init__('auto_explorer')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.create_timer(0.1, self.drive)
        self.front_dist = 10.0
        self.left_dist  = 10.0
        self.right_dist = 10.0
        self.state      = 'forward'
        self.turn_count = 0
        self.turn_dir   = 1.0
        self.get_logger().info('AutoExplorer started!')

    def scan_cb(self, msg):
        ranges = msg.ranges
        n = len(ranges)
        def safe(r): return r if (not math.isnan(r) and not math.isinf(r)) else 10.0
        front_idx = list(range(0, n//8)) + list(range(7*n//8, n))
        left_idx  = list(range(n//8, 3*n//8))
        right_idx = list(range(5*n//8, 7*n//8))
        self.front_dist = min([safe(ranges[i]) for i in front_idx])
        self.left_dist  = min([safe(ranges[i]) for i in left_idx])
        self.right_dist = min([safe(ranges[i]) for i in right_idx])

    def drive(self):
        msg = Twist()
        SAFE = 0.6
        CLOSE = 0.35
        if self.state == 'forward':
            if self.front_dist < SAFE:
                self.state = 'turn'
                self.turn_dir = 1.0 if self.left_dist > self.right_dist else -1.0
                self.turn_count = 0
            else:
                msg.linear.x  = 0.3
                msg.angular.z = 0.05 * (self.left_dist - self.right_dist)
        elif self.state == 'turn':
            if self.front_dist > SAFE + 0.2 and self.turn_count > 10:
                self.state = 'forward'
            else:
                msg.angular.z = 0.6 * self.turn_dir
                self.turn_count += 1
                if self.front_dist < CLOSE:
                    msg.linear.x = -0.1
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AutoExplorer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
