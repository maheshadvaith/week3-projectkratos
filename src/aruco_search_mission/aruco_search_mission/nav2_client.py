import future

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose

class Nav2Client(Node):
    def __init__(self):
        super().__init__('nav2_client')
        self.action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
    
    def send_goal(self, waypoint):
        self.get_logger().info("Waiting for server...")
        self.action_client.wait_for_server()
        
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x = float(waypoint[0])
        goal.pose.pose.position.y = float(waypoint[1])
        goal.pose.pose.orientation.w = 1.0 
        
        self.get_logger().info(f"Dispatching waypoint: x={float(waypoint[0]):.2f}, y={float(waypoint[1]):.2f}")
        
        future = self.action_client.send_goal_async(goal, feedback_callback=self.feedback)
        future.add_done_callback(self.goal_response)

    def feedback(self, msg):
        self.get_logger().info(f"Distance remaining: {msg.feedback.distance_remaining:.2f}, Navigation time: {msg.feedback.navigation_time:.2f}")

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
        else:
            self.get_logger().info("Goal failed.")