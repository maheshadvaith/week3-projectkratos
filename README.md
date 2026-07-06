# Week 3 Assignment - Mission Control GUI

## 1) The GUI:
The GUI is made using PyQT5 and helps the user to dispatch waypoints to the rover and view current status of the rover.
- It includes fields to input three consecutive waypoints
- It includes live position, linear velocity, connection status, angular velocity, distance remaining, mission duration.
- It includes a emergency stop button which stops the rover and cancels all goals
- Log showing errors and live updates

## 2) The node:
- Creates an action client for the `/navigate_to_pose` server
- Sends navigation goals one by one
- Recieves live updates regarding the rover.
- Subscribes to `/odom` for live data
- Uses Twist to stop the rover and cancels all goals

## Dependencies:
- ROS2 Humble
### Python packages:
- PyQT5
- rclpy
### Message types:
- nav2_msgs/action/NAvigateToPose
- nav_msgs/msg/Odometry
- geometry_msgs/msg/Twist

## How to run the project
### 1) Terminal 1 -Get the simulator started
```
cd ~/genesis_sim
source ~/ros2_ws/install/setup.bash
python3 turtlebot_sim.py

```

### 2) Terminal 2 - Start Nav2
```
cd ~/genesis_sim
ros2 launch launch_nav2.py

```
### 3) Terminal 3 - Launch Panel
```
cd ~/ros2_ws
colcon build --packages-select mission_control_gui
source install/setup.bash
ros2 run mission_control_gui mission_gui
```
## Telemetry panel features:
- Includes:
  - A connection status which would help us check if the GUI is connected to the Nav2 action server
  - Live physical coordinates:
    - Position
    - Linear velocity
    - Angular Velocity
  - Distance remaining from the next waypoint
  - Mission duration to check time accurately
  - Emergency stop in case of any unfortunate event, or if you want to change to new waypoints
    

