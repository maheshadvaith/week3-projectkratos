import os
import yaml
import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from action_msgs.msg import GoalStatus
from aruco_search_mission.image_processor import ImageProcessor


class Nav2Client(Node):
    def __init__(self):
        super().__init__('nav2_client')
        self.action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.cmd_vel = self.create_publisher(Twist, "/cmd_vel", 10)
        self.image_processor = ImageProcessor(self)
        self.scan_timer = None

        self.current_x = 0.0
        self.current_y = 0.0
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.waypoints = []
        self.current_waypoint_index = 0
        self.log_path = os.path.join(os.getcwd(), "detected_targets.txt")

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

    def send_goal(self, waypoint):
        self.get_logger().info("Waiting for server...")
        self.action_client.wait_for_server()
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x = float(waypoint["x"])
        goal.pose.pose.position.y = float(waypoint["y"])
        goal.pose.pose.orientation.w = 1.0
        self.get_logger().info(
            f"Dispatching waypoint: x={float(waypoint['x']):.2f}, y={float(waypoint['y']):.2f}"
        )
        future = self.action_client.send_goal_async(goal, feedback_callback=self.feedback)
        future.add_done_callback(self.goal_response)

    def feedback(self, msg):
        self.get_logger().info(f"Distance remaining: {msg.feedback.distance_remaining:.2f}")

    def goal_response(self, future):
        goal_handle = future.result()
        if goal_handle.accepted:
            self.get_logger().info("Goal accepted")
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self.result_response)
        else:
            self.get_logger().info("Goal rejected")

    def result_response(self, future):
        result = future.result()
        self.get_logger().info(f"Status: {result.status}")

        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Goal reached successfully.")
            self.image_processor.searching = True
            self.scan_timer = self.create_timer(0.1, self.rotate_robot)
        else:
            self.get_logger().info("Goal failed.")

    def load_waypoints(self):
        package_dir = get_package_share_directory("aruco_search_mission")
        waypointsfile = os.path.join(package_dir, "config", "aruco_waypoints.yaml")
        with open(waypointsfile, 'r') as f:
            self.waypoints = yaml.safe_load(f)['waypoints']
        self.get_logger().info(f'Loaded {len(self.waypoints)} waypoints.')
        for i in range(len(self.waypoints)):
            self.get_logger().info(f'Waypoint {i}: {self.waypoints[i]}')

    def perform_scan(self):
        self.get_logger().info("Performing scan at current location...")

    def start_mission(self):
        self.get_logger().info("Starting mission...")
        self.current_waypoint_index = 0
        self.send_goal(self.waypoints[self.current_waypoint_index])

    def rotate_robot(self):
        self.get_logger().info(f"found_marker = {self.image_processor.found_marker}")
        msg = Twist()
        msg.angular.z = 0.5
        self.cmd_vel.publish(msg)

        if self.image_processor.found_marker:
            self.scan_timer.cancel()
            self.scan_timer = None
            self.cmd_vel.publish(Twist())
            self.get_logger().info("Starting marker alignment...")

            if self.image_processor.alignment_timer is None:
                self.image_processor.alignment_timer = self.create_timer(
                    0.1,
                    self.image_processor.move_to_marker
                )
            return

    def on_marker_reached(self):
        marker_id = self.image_processor.marker_id
        x = self.current_x
        y = self.current_y

        log_line = f"Target found ID: {marker_id}, Rover Position: ({x:.2f}, {y:.2f})"
        self.get_logger().info(log_line)

        with open(self.log_path, 'a') as f:
            f.write(log_line + "\n")

        self.image_processor.searching = False
        self.image_processor.found_marker = False
        self.image_processor.marker_visible = False
        self.image_processor.aligned = False
        self.image_processor.last_marker_size = 0
        self.image_processor.marker_corners = None
        self.image_processor.marker_id = None
        self.image_processor.last_error = None

        self.current_waypoint_index += 1
        if self.current_waypoint_index < len(self.waypoints):
            self.get_logger().info(
                f"Proceeding to waypoint {self.current_waypoint_index}..."
            )
            self.send_goal(self.waypoints[self.current_waypoint_index])
        else:
            self.get_logger().info("All waypoints complete. Mission finished.")


def main(args=None):
    rclpy.init(args=args)
    node = Nav2Client()
    node.load_waypoints()
    node.start_mission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()