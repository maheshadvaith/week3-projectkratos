import future

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from mission_control_gui.main_window import CreateWindow

class Client(Node):
    def __init__(self):
        super().__init__("nav2_client")
        self.action_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
    

    def send_waypoints(self,waypoints):
        self.current_waypoint = 0
        self.waypoints = waypoints
        self.send_goal(self.waypoints[self.current_waypoint])
        
    
    def send_goal(self, waypoint):
        print(f"Waiting for server...")
        self.action_client.wait_for_server()
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x = float(waypoint[0])
        goal.pose.pose.position.y = float(waypoint[1])
        goal.pose.pose.orientation.w = 1.0 
        future = self.action_client.send_goal_async(goal, feedback_callback=self.feedback)
        future.add_done_callback(self.goal_response)

    def feedback(self,msg):
        print(f"Feedback: distance remaining: {msg.feedback.distance_remaining} m")
    
    
    def goal_response(self,future): 
        self.goal_handle = future.result()
        if self.goal_handle.accepted:
            print("Goal accepted")
            result_future = self.goal_handle.get_result_async()
            result_future.add_done_callback(self.result_response)
        else:
            print("Goal rejected")
    
    def result_response(self,future):
        # if future.result().status == self.goal_handle.STATUS_SUCCEEDED:
        #     print(f"Waypoint {self.current_waypoint + 1} succeeded")
        # else:
        #     print(f"Waypoint {self.current_waypoint + 1} failed")
        print("Result callback reached")
        print(future.result())
        print(future.result().status)
        
        
        self.current_waypoint += 1
        if self.current_waypoint < len(self.waypoints):
            self.send_goal(self.waypoints[self.current_waypoint])
        else:
            print("All waypoints completed")
        
