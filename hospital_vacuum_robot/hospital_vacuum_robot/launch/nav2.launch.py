import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Locate package share and params file so launch works both from source and installed
    pkg_share = get_package_share_directory('hospital_vacuum_robot')
    params_file = os.path.join(pkg_share, 'config', 'nav2_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),

        # Fixed map->odom (robot starts at X=-3, Y=-1)
        # This provides a static transform since we are not using AMCL for simplicity.
        Node(package='tf2_ros', executable='static_transform_publisher',
             name='map_to_odom',
             arguments=['-3', '-1', '0', '0', '0', '0', 'map', 'odom'],
             parameters=[{'use_sim_time': True}]),

        # Map Server: Loads the static map (hospital_map.yaml)
        Node(package='nav2_map_server', executable='map_server',
             name='map_server', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),

        # Controller Server: Generates velocity commands to follow the path
        Node(package='nav2_controller', executable='controller_server',
             name='controller_server', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}],
             remappings=[('cmd_vel', 'cmd_vel_nav')]),

        # Smoother Server: Smooths the generated path
        Node(package='nav2_smoother', executable='smoother_server',
             name='smoother_server', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),

        # Planner Server: Computes the shortest path from A to B
        Node(package='nav2_planner', executable='planner_server',
             name='planner_server', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),

        # Behavior Server: Handles recovery behaviors (e.g., spinning, backing up)
        Node(package='nav2_behaviors', executable='behavior_server',
             name='behavior_server', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),

        # BT Navigator: The core decision maker (Behavior Tree)
        Node(package='nav2_bt_navigator', executable='bt_navigator',
             name='bt_navigator', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),

        # Waypoint Follower: Allows sending multiple goals
        Node(package='nav2_waypoint_follower', executable='waypoint_follower',
             name='waypoint_follower', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),

        # Velocity Smoother: Ensures smooth acceleration/deceleration
        Node(package='nav2_velocity_smoother', executable='velocity_smoother',
             name='velocity_smoother', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}],
             remappings=[('cmd_vel', 'cmd_vel_nav'),
                         ('cmd_vel_smoothed', 'cmd_vel')]),

        # Collision Monitor: Stops the robot if an obstacle suddenly appears
        Node(package='nav2_collision_monitor', executable='collision_monitor',
             name='collision_monitor', output='screen',
             parameters=[params_file, {'use_sim_time': use_sim_time}]),

        # Lifecycle Manager: Starts all the above nodes in the correct order
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_navigation', output='screen',
             parameters=[{'use_sim_time': use_sim_time, 'autostart': True,
                          'node_names': ['map_server', 'controller_server',
                                         'smoother_server', 'planner_server',
                                         'behavior_server', 'bt_navigator',
                                         'waypoint_follower', 'velocity_smoother',
                                         'collision_monitor']}]),
    ])