import os 
import yaml
import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from ament_index_python.packages import get_package_share_directory
from aruco_search_mission.nav2_client import Nav2Client

class SearchNode(Node):
    def __init__(self):
        super().__init__('mission_node')
        self.nav2_client = Nav2Client()
        self.load_waypoints()
        self.start_mission()
        
        
    
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
        self.nav2_client.send_goal(self.waypoints[0])
        self.perform_scan()
        
def main(args=None):
        rclpy.init(args = args)
        
        node = SearchNode()
        rclpy.spin(node)
        
        
        
        
        node.destroy_node()
        rclpy.shutdown()
    
if __name__ == '__main__':
    main()    
        
        
