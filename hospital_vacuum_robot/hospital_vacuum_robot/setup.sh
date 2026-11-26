#!/usr/bin/env bash
# =============================================================
# hospital_vacuum_robot — WSL2 / ROS2 Jazzy Setup Script
# Run this ONCE after extracting the package.
# =============================================================
set -e

echo ""
echo "========================================================"
echo "  Hospital Vacuum Robot — WSL2 Setup"
echo "  ROS2 Jazzy + Gz Sim (Gazebo Harmonic)"
echo "========================================================"
echo ""

# ── 1. Source ROS2 ─────────────────────────────────────────
source /opt/ros/jazzy/setup.bash

# ── 2. Add ROS2 apt repo (in case it's missing) ────────────
sudo apt install -y software-properties-common curl
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update

# ── 3. Install Gz Sim (Gazebo Harmonic) for Jazzy ──────────
echo ""
echo ">>> Installing Gazebo Harmonic (ros_gz) for ROS2 Jazzy..."
sudo apt install -y \
  gz-harmonic \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-interfaces \
  || echo "⚠️  gz-harmonic not found, trying alternative..."

# Alternative package names
sudo apt install -y \
  ros-jazzy-gz-sim-vendor \
  || true

# ── 4. Core ROS2 tools ──────────────────────────────────────
echo ""
echo ">>> Installing ROS2 core tools..."
sudo apt install -y \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-tf2-tools \
  ros-jazzy-tf2-ros \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-rviz2

# ── 5. Build tools ──────────────────────────────────────────
sudo apt install -y python3-colcon-common-extensions python3-rosdep

# ── 6. rosdep init (skip if already done) ──────────────────
sudo rosdep init 2>/dev/null || true
rosdep update

# ── 7. Create workspace if missing ─────────────────────────
mkdir -p ~/ros2_ws/src

# ── 8. Copy package ────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$SCRIPT_DIR" != "$HOME/ros2_ws/src/hospital_vacuum_robot" ]; then
  cp -r "$SCRIPT_DIR" ~/ros2_ws/src/hospital_vacuum_robot
  echo "✓ Copied package to ~/ros2_ws/src/hospital_vacuum_robot"
fi

# ── 9. Make Python nodes executable ────────────────────────
chmod +x ~/ros2_ws/src/hospital_vacuum_robot/hospital_vacuum_robot/*.py
echo "✓ Python nodes marked executable"

# ── 10. Install rosdep dependencies ────────────────────────
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y 2>/dev/null || true

# ── 11. Build ───────────────────────────────────────────────
echo ""
echo ">>> Building hospital_vacuum_robot..."
colcon build --packages-select hospital_vacuum_robot --symlink-install
source install/setup.bash
echo "✓ Build complete"

# ── 12. Add to .bashrc ──────────────────────────────────────
BASHRC="$HOME/.bashrc"
if ! grep -q "ros2_ws" "$BASHRC"; then
  cat >> "$BASHRC" << 'BASHRC_BLOCK'

# === ROS2 Jazzy ===
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
export DISPLAY=:0
export LIBGL_ALWAYS_SOFTWARE=1
BASHRC_BLOCK
  echo "✓ Added ROS2 sourcing to ~/.bashrc"
fi

echo ""
echo "========================================================"
echo "  ✅ Setup complete!"
echo ""
echo "  NEXT STEPS:"
echo ""
echo "  1. Launch simulation:"
echo "     ros2 launch hospital_vacuum_robot simulation.launch.py"
echo ""
echo "  2. Keyboard control (new terminal):"
echo "     ros2 run teleop_twist_keyboard teleop_twist_keyboard"
echo ""
echo "  3. Activate UV-C sterilizer (stopped robot only):"
echo "     ros2 topic pub /sterilize_on std_msgs/Bool 'data: true' --once"
echo ""
echo "  4. Visualize in RViz2:"
echo "     rviz2"
echo "========================================================"
