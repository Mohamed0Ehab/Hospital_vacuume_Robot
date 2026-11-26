# 🏥 Hospital Vacuum Robot — Complete Setup Guide
## ROS2 Jazzy + Gazebo on WSL2

---

## 📦 Project Structure

```
hospital_vacuum_robot/
├── CMakeLists.txt
├── package.xml
├── hospital_vacuum_robot/
│   ├── __init__.py
│   ├── diff_drive_kinematics.py     ← Main kinematics node
│   └── sterilization_controller.py  ← UV-C safety controller
├── urdf/
│   └── vacuum_robot.urdf.xacro      ← Full robot description
├── launch/
│   └── simulation.launch.py         ← Main launch file
└── worlds/
    └── hospital_room.world           ← Gazebo hospital room
```

---

## STEP 1 — Install Dependencies in WSL2

Open your WSL terminal and run:

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# ROS2 Jazzy core (if not installed)
sudo apt install -y ros-jazzy-desktop

# Gazebo + ROS bridge
sudo apt install -y ros-jazzy-gazebo-ros-pkgs \
                    ros-jazzy-gazebo-ros2-control

# Teleop keyboard
sudo apt install -y ros-jazzy-teleop-twist-keyboard

# TF2 and nav tools
sudo apt install -y ros-jazzy-tf2-tools \
                    ros-jazzy-nav2-msgs \
                    ros-jazzy-rqt-robot-steering

# Xacro
sudo apt install -y ros-jazzy-xacro

# Python deps
pip3 install transforms3d
```

---

## STEP 2 — Create the Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Copy the hospital_vacuum_robot package here
# (move the folder you downloaded)
cp -r /path/to/hospital_vacuum_robot .
```

---

## STEP 3 — Make Python nodes executable

```bash
cd ~/ros2_ws/src/hospital_vacuum_robot

chmod +x hospital_vacuum_robot/diff_drive_kinematics.py
chmod +x hospital_vacuum_robot/sterilization_controller.py
```

---

## STEP 4 — Build the Package

```bash
cd ~/ros2_ws

# Source ROS2
source /opt/ros/jazzy/setup.bash

# Build
colcon build --packages-select hospital_vacuum_robot

# Source your workspace
source install/setup.bash
```

---

## STEP 5 — Enable Gazebo in WSL2 (GUI support)

Add this to your `~/.bashrc`:

```bash
# Paste these lines at the bottom of ~/.bashrc
export DISPLAY=:0
export LIBGL_ALWAYS_SOFTWARE=1          # if no GPU passthrough
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/usr/share/gazebo-11/models
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

Then reload:
```bash
source ~/.bashrc
```

> **Note:** On Windows 11 with WSLg, Gazebo GUI opens automatically.  
> On Windows 10, install VcXsrv or use X410 as your X server.

---

## STEP 6 — Launch the Simulation

```bash
# Terminal 1 — Launch everything
ros2 launch hospital_vacuum_robot simulation.launch.py
```

Wait ~5 seconds for Gazebo to open and the robot to spawn.

---

## STEP 7 — Keyboard Control 🎮

```bash
# Terminal 2 — Keyboard teleop
source ~/ros2_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Controls:
| Key        | Action              |
|------------|---------------------|
| `w`        | Move forward        |
| `s`        | Move backward       |
| `a`        | Rotate left         |
| `d`        | Rotate right        |
| `q`        | Forward + left arc  |
| `e`        | Forward + right arc |
| `x`        | Stop                |
| `+` / `-`  | Speed up / slow down|
| `CTRL+C`   | Quit                |

---

## STEP 8 — Activate UV-C Sterilization

```bash
# Terminal 3 — Activate sterilization (robot must be stopped first!)
source ~/ros2_ws/install/setup.bash
ros2 topic pub /sterilize_on std_msgs/Bool "data: true" --once

# Deactivate
ros2 topic pub /sterilize_on std_msgs/Bool "data: false" --once

# Check status
ros2 topic echo /sterilize_status
```

---

## STEP 9 — Monitor Robot State

```bash
# View odometry
ros2 topic echo /odom

# View laser scan
ros2 topic echo /scan

# Check TF tree
ros2 run tf2_tools view_frames

# RViz2 visualization
rviz2

# Add displays in RViz:
#  - Fixed Frame: odom
#  - Add → LaserScan → topic: /scan
#  - Add → Odometry → topic: /odom
#  - Add → TF
```

---

## How the Kinematics Work (Modern Robotics)

### Inverse Kinematics — cmd_vel → wheel speeds

```
Given: v (linear m/s), ω (angular rad/s)
       r = wheel radius, d = half wheel separation

ω_L = (v - ω·d) / r    [left wheel rad/s]
ω_R = (v + ω·d) / r    [right wheel rad/s]
```

### Forward Kinematics — wheel speeds → pose update

```
v_body  = r/2 · (ω_R + ω_L)         [m/s]
ω_body  = r/(2d) · (ω_R - ω_L)      [rad/s]

Δs      = v_body · dt
Δθ      = ω_body · dt

x      += Δs · cos(θ + Δθ/2)        ← midpoint integration
y      += Δs · sin(θ + Δθ/2)
θ      += Δθ
```

The **midpoint method** (RK2) is more accurate than simple Euler integration — it's what Modern Robotics §13 recommends for differential drive.

---

## Preparing for Future Upgrades

### Nav2 / SLAM (next step)
```bash
sudo apt install -y ros-jazzy-slam-toolbox ros-jazzy-nav2-bringup
# Then add a Nav2 launch to your simulation.launch.py
```

### micro-ROS (ESP32)
```bash
sudo apt install -y ros-jazzy-micro-ros-agent
# Flash micro-ROS firmware on ESP32
# Run: ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
# The ESP32 will publish /left_wheel_vel and /right_wheel_vel
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Gazebo doesn't open | Check `DISPLAY=:0` and your X server |
| `xacro` error | Run `sudo apt install ros-jazzy-xacro` |
| Robot falls through floor | Increase `<kp>` in URDF wheel Gazebo tags |
| No `/scan` topic | Check Gazebo lidar plugin is loaded |
| `colcon build` fails | Source ROS2 first: `source /opt/ros/jazzy/setup.bash` |
| Kinematics node not found | Run `colcon build` then `source install/setup.bash` |

---

*Built for ROS2 Jazzy + Gazebo Classic | Modern Robotics principles*
