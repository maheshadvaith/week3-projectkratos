import future

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from mission_control_gui.main_window import CreateWindow
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from action_msgs.msg import GoalStatus

class Client(Node):
    def __init__(self):
        super().__init__("nav2_client")
        self.action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.odom_sub = self.create_subscription(Odometry, "/odom", self.odom_callback, 10)
        self.cmd_vel = self.create_publisher(Twist, "/cmd_vel", 10)
        self.emergency_stop = False
        
    def send_waypoints(self,waypoints):
        self.emergency_stop = False
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
        self.logger.log.emit(
        f"Dispatching waypoint {self.current_waypoint + 1}/{len(self.waypoints)}: "f"x={float(waypoint[0]):.2f}, y={float(waypoint[1]):.2f}")
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
        if self.emergency_stop:
            self.logger.log.emit("Mission aborted.")
            self.emergency_stop = False
            return
        
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.logger.log.emit(f"Waypoint {self.current_waypoint + 1} SUCCEEDED")
        elif status == GoalStatus.STATUS_CANCELED:
            self.logger.log.emit(f"Waypoint {self.current_waypoint + 1} CANCELLED")
        else:
            self.logger.log.emit(f"Waypoint {self.current_waypoint + 1} FAILED")
            
        self.current_waypoint += 1
        if self.current_waypoint < len(self.waypoints):
            self.send_goal(self.waypoints[self.current_waypoint])
        else:
            self.logger.log.emit("All waypoints completed")
    
    def odom_callback(self, msg):
        self.window.update_position_textlabel(msg.pose.pose.position.x, msg.pose.pose.position.y,msg.twist.twist.linear.x, msg.twist.twist.angular.z)

    def cancel_all_goals(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.z = 0.0
        self.cmd_vel.publish(msg)
        self.logger.log.emit("Emergency Stop Activated")
        self.emergency_stop = True
        if hasattr(self, 'goal_handle'):
            self.goal_handle.cancel_goal_async()
            
        else:
            self.logger.log.emit("No goal to cancel")
    

    
    