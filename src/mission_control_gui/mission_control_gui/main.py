import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from PyQt5.QtWidgets import QApplication

from mission_control_gui.main_window import CreateWindow, LogEmitter
from mission_control_gui.nav2_client import Client

import threading


    



def main():
    rclpy.init()

    nav2_client = Client()

    app = QApplication([])
    window = CreateWindow(nav2_client)
    logger = LogEmitter()
    logger.log.connect(window.LogsText.append)
    nav2_client.logger = logger
    
    nav2_client.window = window
    window.show()
    ros_thread = threading.Thread(target=rclpy.spin, args=(nav2_client,), daemon=True)
    ros_thread.start()
    
    app.exec_()
    nav2_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()