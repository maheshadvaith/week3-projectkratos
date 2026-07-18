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
    
        if self.found_marker:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        corners, ids, _ = self.detector.detectMarkers(frame)

    
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        
            self.marker_corners = corners[0]
            self.marker_id = int(ids[0][0])
            self.found_marker = True

            self.node.get_logger().info(
            f"ArUco marker detected! ID: {self.marker_id}"
        )

        cv2.imshow("Robot Camera", frame)
        cv2.waitKey(1)
