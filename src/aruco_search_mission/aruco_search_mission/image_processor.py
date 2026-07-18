from gs_ros_interfaces import msg
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImageProcessor:
    def __init__(self,node):
        self.node = node
        self.bridge = CvBridge()
        self.image_subscriber = self.node.create_subscription(
            Image,
            '/turtlebot/rgb',
            self.image_callback,
            10
        )
        self.latest_image = None
        self.found_marker = False
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
        self.detector = cv2.aruco.ArucoDetector(self.dictionary, cv2.aruco.DetectorParameters())
        
    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        cv2.imshow("Robot Camera", frame)
        cv2.waitKey(1)

        corners, ids, rejected = self.detector.detectMarkers(frame)

        self.node.get_logger().info(
            f"ids={ids}, rejected={len(rejected)}"
        )
