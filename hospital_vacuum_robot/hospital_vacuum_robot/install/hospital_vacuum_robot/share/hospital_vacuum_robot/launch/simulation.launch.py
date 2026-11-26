import os
import shlex
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('hospital_vacuum_robot')
    urdf_path  = os.path.join(pkg, 'urdf',   'vacuum_robot.urdf.xacro')
    world_path = os.path.join(pkg, 'worlds', 'hospital_room.world')

    # Quote the URDF path explicitly and include a separating space so the final
    # shell command becomes: xacro '/full/path/with spaces/...'
    quoted_urdf_path = "'{}'".format(urdf_path)
    robot_description = ParameterValue(Command(['xacro ', quoted_urdf_path]), value_type=str)

    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Run Gz Sim with -s flag (server only, no GUI) for WSL performance
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-s', world_path],
        output='screen'
    )

    # Gz GUI separately (optional, comment out if too slow)
    gazebo_gui = ExecuteProcess(
        cmd=['gz', 'sim', '-g'],
        output='screen'
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}]
    )

    jsp = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_footprint_to_odom',
        arguments=['--x', '0', '--y', '0', '--z', '0',
                   '--roll', '0', '--pitch', '0', '--yaw', '0',
                   '--frame-id', 'odom',
                   '--child-frame-id', 'base_footprint'],
        output='screen'
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', '-name', 'vacuum_robot',
                   '-x', '0.0', '-y', '0.0', '-z', '0.10'],
        output='screen'
    )

    kinematics = Node(
        package='hospital_vacuum_robot',
        executable='diff_drive_kinematics.py',
        name='diff_drive_kinematics',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    sterilizer = Node(
        package='hospital_vacuum_robot',
        executable='sterilization_controller.py',
        name='sterilization_controller',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        use_sim_time_arg,
        gazebo,
        rsp,
        jsp,
        static_tf,
        TimerAction(period=3.0, actions=[spawn]),
        TimerAction(period=5.0, actions=[kinematics]),
        TimerAction(period=5.0, actions=[sterilizer]),
        TimerAction(period=6.0, actions=[gazebo_gui]),
    ])
