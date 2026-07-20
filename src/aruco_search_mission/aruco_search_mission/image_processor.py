from gs_ros_interfaces import msg
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

import numpy as np
from geometry_msgs.msg import Twist


class ImageProcessor:
    def __init__(self, node):
        self.node = node
        self.bridge = CvBridge()
        self.image_subscriber = self.node.create_subscription(
            Image,
            '/turtlebot/rgb',
            self.image_callback,
            10
        )
        self.searching = False
        self.aligned = False
        self.alignment_timer = None
        self.cmd_vel = self.node.create_publisher(Twist, "/cmd_vel", 10)
        self.latest_image = None
        self.found_marker = False
        self.last_error = None
        self.marker_visible = False
        self.marker_corners = None
        self.marker_id = None
        self.last_marker_size = 0
        self.image_width = None
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
        self.detector = cv2.aruco.ArucoDetector(self.dictionary, cv2.aruco.DetectorParameters())

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        self.image_width = frame.shape[1]
        if not self.searching:
            cv2.imshow("Robot Camera", frame)
            cv2.waitKey(1)
            return
        corners, ids, _ = self.detector.detectMarkers(frame)

        if ids is not None:
            self.marker_corners = corners[0]
            self.marker_id = int(ids[0][0])
            self.marker_visible = True
            if not self.found_marker:
                self.found_marker = True
                self.node.get_logger().info(f"ArUco marker detected! ID: {self.marker_id}")
        else:
            self.marker_visible = False

        cv2.imshow("Robot Camera", frame)
        cv2.waitKey(1)
        
    def move_to_marker(self):
        if not self.found_marker:
            return


        if not self.marker_visible:
            if self.last_marker_size >= 127:
                self.node.get_logger().info(
                    f"Marker lost near target range (last size={self.last_marker_size:.1f}) — treating as reached."
                )
                self.cmd_vel.publish(Twist())
                self.alignment_timer.cancel()
                self.alignment_timer = None
                self.node.on_marker_reached()
                return
            else:
                
                self.node.get_logger().info(
                    f"Marker not visible (last size={self.last_marker_size:.1f}) — recovering."
                )
                msg = Twist()
                msg.angular.z = 0.1 if self.last_error is not None and self.last_error < 0 else -0.1
                self.cmd_vel.publish(msg)
                return

        points = self.marker_corners.reshape((4, 2))
        center_x = int(points[:, 0].mean())

        top = np.linalg.norm(points[0] - points[1])
        right = np.linalg.norm(points[1] - points[2])
        bottom = np.linalg.norm(points[2] - points[3])
        left = np.linalg.norm(points[3] - points[0])
        marker_size = (top + right + bottom + left) / 4
        self.last_marker_size = marker_size

        error = center_x - (self.image_width / 2)
        self.last_error = error
        msg = Twist()

        if abs(error) > 15:
            self.aligned = False
            msg.angular.z = -0.15 if error > 0 else 0.15
            self.cmd_vel.publish(msg)
            return

        self.aligned = True

        if marker_size < 150:
            self.node.get_logger().info(f"marker_size={marker_size:.1f}")
            msg.linear.x = 0.08
            self.cmd_vel.publish(msg)
            return

        self.cmd_vel.publish(Twist())
        self.alignment_timer.cancel()
        self.alignment_timer = None
        self.node.get_logger().info("Reached marker.")
        self.node.on_marker_reached()