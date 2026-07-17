
import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from ament_index_python.packages import get_package_share_directory
from aruco_search_mission.nav2_client import Nav2Client


    
        
def main(args=None):
        rclpy.init(args = args)
        
        nav2_client = Nav2Client() 
        nav2_client.load_waypoints()
        nav2_client.start_mission()
        rclpy.spin(nav2_client)
        
        nav2_client.destroy_node()
        rclpy.shutdown()
    
if __name__ == '__main__':
    main()    
        
        
