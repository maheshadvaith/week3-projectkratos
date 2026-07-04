import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from PyQt5.QtWidgets import QApplication
from mission_control_gui.main_window import CreateWindow




def main():
    app = QApplication([])
    window = CreateWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()