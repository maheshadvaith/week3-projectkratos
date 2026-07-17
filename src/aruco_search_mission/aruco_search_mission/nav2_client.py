import future

import os 
import yaml
import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from ament_index_python.packages import get_package_share_directory


class Nav2Client(Node):
    def __init__(self):
        super().__init__('nav2_client')
        self.action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        
    def send_goal(self, waypoint):
        self.get_logger().info("Waiting for server...")
        self.action_client.wait_for_server()
        
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x = float(waypoint["x"])
        goal.pose.pose.position.y = float(waypoint["y"])
        goal.pose.pose.orientation.w = 1.0 
        
        self.get_logger().info(f"Dispatching waypoint: x={float(waypoint['x']):.2f}, y={float(waypoint['y']):.2f}")
        
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
        result = future.result().result
        if result:
            self.get_logger().info("Goal reached successfully.")
            self.perform_scan()
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
        self.send_goal(self.waypoints[0])
        