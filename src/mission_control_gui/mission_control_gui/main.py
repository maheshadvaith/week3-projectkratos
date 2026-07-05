import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from PyQt5.QtWidgets import QApplication

from mission_control_gui.main_window import CreateWindow
from mission_control_gui.nav2_client import Client




def main():
    rclpy.init()

    nav2_client = Client()

    app = QApplication([])
    window = CreateWindow(nav2_client)
    nav2_client.window = window
    window.show()
    app.exec_()
    rclpy.spin(nav2_client)
    rclpy.shutdown()

if __name__ == '__main__':
    main()