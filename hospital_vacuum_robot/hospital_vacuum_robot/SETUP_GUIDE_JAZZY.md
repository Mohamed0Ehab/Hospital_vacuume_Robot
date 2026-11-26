# 🏥 Hospital Vacuum Robot — Corrected Setup for ROS2 Jazzy (WSL2)

## ❗ What Was Wrong & Why

| Error | Cause | Fix |
|---|---|---|
| `No module named 'ament_python'` | Wrong import in launch file | Use `ament_index_python` instead |
| `ros-jazzy-gazebo-ros-pkgs` not found | Jazzy uses **Gz Sim (Gazebo Harmonic)**, NOT Gazebo Classic | Install `ros-jazzy-ros-gz` |

---

## STEP 1 — Install the Right Gazebo for Jazzy

ROS2 Jazzy ships with **Gazebo Harmonic** (also called `gz-harmonic` or `ros_gz`).  
Gazebo Classic (`gazebo_ros`) is **NOT available** for Jazzy.

```bash
sudo apt update

# Gazebo Harmonic + ROS bridge
sudo apt install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-interfaces

# Core tools
sudo apt install -y \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-tf2-tools \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-rviz2
```

> ⚠️ If `ros-jazzy-ros-gz` is missing too, run the **automatic setup script** instead:
> ```bash
> bash ~/ros2_ws/src/hospital_vacuum_robot/setup.sh
> ```

---

## STEP 2 — Place the Package

```bash
mkdir -p ~/ros2_ws/src
# Move/copy the extracted folder:
cp -r /path/to/hospital_vacuum_robot ~/ros2_ws/src/
```

---

## STEP 3 — Make Nodes Executable

```bash
chmod +x ~/ros2_ws/src/hospital_vacuum_robot/hospital_vacuum_robot/*.py
```

---

## STEP 4 — Build

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select hospital_vacuum_robot --symlink-install
source install/setup.bash
```

---

## STEP 5 — Add to ~/.bashrc (do once)

```bash
echo "source /opt/ros/jazzy/setup.bash"   >> ~/.bashrc
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
echo "export DISPLAY=:0"                   >> ~/.bashrc
echo "export LIBGL_ALWAYS_SOFTWARE=1"      >> ~/.bashrc
source ~/.bashrc
```

---

## STEP 6 — Launch Simulation

```bash
# Terminal 1
ros2 launch hospital_vacuum_robot simulation.launch.py
```

Gz Sim (Gazebo Harmonic) will open with the hospital room world.  
The robot spawns after ~2 seconds.

---

## STEP 7 — Keyboard Control

```bash
# Terminal 2
source ~/.bashrc
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

| Key | Action |
|-----|--------|
| `w` | Forward |
| `s` | Backward |
| `a` | Rotate left |
| `d` | Rotate right |
| `x` | Stop |
| `q/e` | Arc turns |

---

## STEP 8 — UV-C Sterilization

```bash
# Terminal 3 — activate (robot must be stopped)
ros2 topic pub /sterilize_on std_msgs/Bool "data: true" --once

# Deactivate
ros2 topic pub /sterilize_on std_msgs/Bool "data: false" --once

# Monitor status
ros2 topic echo /sterilize_status
```

---

## STEP 9 — View in RViz2

```bash
# Terminal 4
rviz2
```

Inside RViz2:
1. Set **Fixed Frame** → `odom`
2. **Add** → `TF`
3. **Add** → `LaserScan` → topic: `/scan`
4. **Add** → `Odometry` → topic: `/odom`
5. **Add** → `RobotModel` → description topic: `/robot_description`

---

## Useful Debug Commands

```bash
# Check all topics are publishing
ros2 topic list

# Verify odometry
ros2 topic echo /odom --once

# Check TF tree
ros2 run tf2_tools view_frames

# Check nodes running
ros2 node list

# Republish odom → Gz bridge (if needed)
ros2 run ros_gz_bridge parameter_bridge /odom@nav_msgs/msg/Odometry@gz.msgs.Odometry
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ros-jazzy-ros-gz` not found | Run `sudo apt update` first, check ROS2 repo is added |
| Gz Sim won't open | Try `export LIBGL_ALWAYS_SOFTWARE=1` for WSL GPU issues |
| Robot falls through floor | Increase `<kp>` in URDF wheel Gazebo tags to `1000000` |
| `xacro` error on build | `sudo apt install ros-jazzy-xacro` |
| `joint_state_publisher` missing | `sudo apt install ros-jazzy-joint-state-publisher` |
| Kinematics node crashes | Check: `ros2 run hospital_vacuum_robot diff_drive_kinematics.py` directly |
| No `/scan` topic | Gz sensor bridge: `ros2 run ros_gz_bridge parameter_bridge /scan@sensor_msgs/msg/LaserScan` |

---

## Jazzy vs Humble: Key Differences

| Feature | ROS2 Humble | ROS2 Jazzy |
|---------|------------|-----------|
| Gazebo | Classic (`gazebo_ros`) | Harmonic (`ros_gz`) |
| Gazebo pkg | `ros-humble-gazebo-ros-pkgs` | `ros-jazzy-ros-gz` |
| Spawn entity | `spawn_entity.py` | `ros_gz_sim create` |
| Launch | `gazebo.launch.py` | `gz_sim.launch.py` |
| World bridge | built-in | `ros_gz_bridge` |
