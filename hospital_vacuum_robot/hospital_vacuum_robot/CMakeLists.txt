cmake_minimum_required(VERSION 3.8)
project(hospital_vacuum_robot)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  hospital_vacuum_robot/diff_drive_kinematics.py
  hospital_vacuum_robot/sterilization_controller.py
  hospital_vacuum_robot/obstacle_avoidance.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY urdf launch worlds config maps
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

install(PROGRAMS
  hospital_vacuum_robot/auto_explorer.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME auto_explorer
)

install(PROGRAMS
  hospital_vacuum_robot/auto_explorer.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME auto_explorer
)
