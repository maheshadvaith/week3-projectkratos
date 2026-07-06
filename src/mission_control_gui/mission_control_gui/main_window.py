from PyQt5.QtWidgets import QMainWindow, QApplication,QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import QObject, pyqtSignal

class LogEmitter(QObject):
    log = pyqtSignal(str)
    





class CreateWindow(QMainWindow):
    def __init__(self, nav2_client):
        super().__init__()
        self.nav2_client = nav2_client
        
        self.setWindowTitle("Mission Control GUI")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        grid = QGridLayout()
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)
        
        self.waypoint1 = QLabel("Waypoint 1:")
        self.waypoint1X = QLineEdit()
        self.waypoint1Y = QLineEdit()

        self.waypoint2 = QLabel("Waypoint 2:")
        self.waypoint2X = QLineEdit()
        self.waypoint2Y = QLineEdit()

        self.waypoint3 = QLabel("Waypoint 3:")
        self.waypoint3X = QLineEdit()
        self.waypoint3Y = QLineEdit()

        grid.addWidget(self.waypoint1, 0, 0)
        grid.addWidget(self.waypoint1X, 0, 1)
        grid.addWidget(self.waypoint1Y, 0, 2)

        grid.addWidget(self.waypoint2, 1, 0)
        grid.addWidget(self.waypoint2X, 1, 1)
        grid.addWidget(self.waypoint2Y, 1, 2)

        grid.addWidget(self.waypoint3, 2, 0)
        grid.addWidget(self.waypoint3X, 2, 1)
        grid.addWidget(self.waypoint3Y, 2,2)

        self.SubmitButton = QPushButton("Submit")
        grid.addWidget(self.SubmitButton, 3,1)

        self.Logs = QLabel("Logs:")
        self.LogsText = QTextEdit()
        grid.addWidget(self.Logs, 4, 0)
        grid.addWidget(self.LogsText, 4, 1, 1, 2)

        self.SubmitButton.clicked.connect(self.submit)
        
        # Telemetry part:
        self.TelemetryLabel = QLabel("Rover Status:")
        grid.addWidget(self.TelemetryLabel, 0,3)
        
        self.ConnectionLabel = QLabel("Connection Status: Disconnected")
        grid.addWidget(self.ConnectionLabel, 1,3)
        
        self.PositionLabel = QLabel("Position: (0.0, 0.0)")
        grid.addWidget(self.PositionLabel, 2,3)
        
        self.linearVelocityLabel = QLabel("Linear Velocity: 0 m/s")
        grid.addWidget(self.linearVelocityLabel, 3,3)
        
        self.angularVelocityLabel = QLabel("Angular Velocity: 0 rad/s")
        grid.addWidget(self.angularVelocityLabel, 4,3)
        
        self.DistanceLeft = QLabel("Distance Left: 0 m")
        grid.addWidget(self.DistanceLeft, 5,3)
        
        self.MissionDuration = QLabel("Mission Duration: 0 s")
        grid.addWidget(self.MissionDuration, 6,3)
        
        self.EmergencyStopButton = QPushButton("Emergency Stop")
        grid.addWidget(self.EmergencyStopButton,3,2)
        
        self.EmergencyStopButton.clicked.connect(self.emergency_stop)

    def emergency_stop(self):
        self.nav2_client.cancel_all_goals()
        self.LogsText.append("Emergency Stop Activated")
        self.update_connection_textlabel(False)
    
    
    def submit(self):
            waypoint1 = [self.waypoint1X.text(), self.waypoint1Y.text()]
            waypoint2 = [self.waypoint2X.text(), self.waypoint2Y.text()]
            waypoint3 = [self.waypoint3X.text(), self.waypoint3Y.text()]    
            self.LogsText.append(f"Submitted Waypoints: {waypoint1}, {waypoint2}, {waypoint3}")

            if(self.validate_waypoints(self.waypoint1X.text(), self.waypoint1Y.text()) and self.validate_waypoints(self.waypoint2X.text(), self.waypoint2Y.text()) and self.validate_waypoints(self.waypoint3X.text(), self.waypoint3Y.text())):
                self.LogsText.append("Valid waypoints")
                waypoints = [waypoint1, waypoint2, waypoint3]
                self.nav2_client.send_waypoints(waypoints)
            else:
                self.LogsText.append("Invalid waypoints")  

            
    def validate_waypoints(self,x,y):

        try:
            x = float(x.strip())
            y = float(y.strip())
            return True
        except ValueError:
            return False
        
    def update_connection_textlabel(self, connected):
        if connected:
            self.ConnectionLabel.setText("Connection Status: Connected")
        else:
            self.ConnectionLabel.setText("Connection Status: Disconnected")
        
        
    def update_position_textlabel(self, x, y, linear_velocity, angular_velocity):
        self.PositionLabel.setText(f"Position: ({x:.2f}, {y:.2f})")
        
        self.linearVelocityLabel.setText(f"Linear Velocity: {linear_velocity:.2f} m/s")
        self.angularVelocityLabel.setText(f"Angular Velocity: {angular_velocity:.2f} rad/s")
        
    def update_other(self, distance_remaining, mission_duration):
        self.DistanceLeft.setText(f"Distance Left: {distance_remaining:.2f} m")
        self.MissionDuration.setText(f"Mission Duration: {mission_duration.sec:.2f} s")