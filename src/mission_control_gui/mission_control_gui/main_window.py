from PyQt5.QtWidgets import QMainWindow, QApplication

class CreateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mission Control GUI")
        self.setGeometry(100, 100, 800, 600)

