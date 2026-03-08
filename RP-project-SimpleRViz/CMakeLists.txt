cmake_minimum_required(VERSION 3.8)
project(simple_rviz_clone)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(OpenCV REQUIRED)
find_package(nav2_msgs REQUIRED)

# Include directories
include_directories(include)

# Executable
add_executable(simple_rviz_node 
  src/main.cpp 
  src/visualizer.cpp
)

add_executable(mouse_test src/mouse_test.cpp)

ament_target_dependencies(simple_rviz_node
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
  tf2_ros
  tf2_geometry_msgs
  nav2_msgs
)

target_link_libraries(simple_rviz_node ${OpenCV_LIBS})
target_link_libraries(mouse_test ${OpenCV_LIBS})

# Install
install(TARGETS
  simple_rviz_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY include/
  DESTINATION include/)
  
install(TARGETS mouse_test DESTINATION lib/${PROJECT_NAME})

ament_package()
