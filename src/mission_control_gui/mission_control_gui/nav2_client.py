import future

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from mission_control_gui.main_window import CreateWindow
from nav_msgs.msg import Odometry

class Client(Node):
    def __init__(self):
        super().__init__("nav2_client")
        self.action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.odom_sub = self.create_subscription(Odometry, "/odom", self.odom_callback, 10)

    def send_waypoints(self,waypoints):
        self.current_waypoint = 0
        self.waypoints = waypoints
        self.send_goal(self.waypoints[self.current_waypoint])
        
    
    def send_goal(self, waypoint):
        self.logger.log.emit(f"Waiting for server...")
        self.action_client.wait_for_server()
        self.window.update_connection_textlabel(True)
        
        
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x = float(waypoint[0])
        goal.pose.pose.position.y = float(waypoint[1])
        goal.pose.pose.orientation.w = 1.0 
        future = self.action_client.send_goal_async(goal, feedback_callback=self.feedback)
        future.add_done_callback(self.goal_response)

    def feedback(self,msg):
        self.window.update_other(msg.feedback.distance_remaining, msg.feedback.navigation_time)
    
    
    def goal_response(self,future): 
        self.goal_handle = future.result()
        if self.goal_handle.accepted:
            self.logger.log.emit("Goal accepted")
            result_future = self.goal_handle.get_result_async()
            result_future.add_done_callback(self.result_response)
        else:
            self.logger.log.emit("Goal rejected")
    
    def result_response(self,future):
        # if future.result().status == self.goal_handle.STATUS_SUCCEEDED:
        #     print(f"Waypoint {self.current_waypoint + 1} succeeded")
        # else:
        #     print(f"Waypoint {self.current_waypoint + 1} failed")
        self.logger.log.emit("Result callback reached")
        
        
        
        self.current_waypoint += 1
        if self.current_waypoint < len(self.waypoints):
            self.send_goal(self.waypoints[self.current_waypoint])
        else:
            self.logger.log.emit("All waypoints completed")
    
    def odom_callback(self, msg):
        self.window.update_position_textlabel(msg.pose.pose.position.x, msg.pose.pose.position.y,msg.twist.twist.linear.x, msg.twist.twist.angular.z)

    
    