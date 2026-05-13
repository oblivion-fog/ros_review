cmake_minimum_required(VERSION 3.8)
project(exercise)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(turtlesim REQUIRED)
find_package(base_interface REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp_action REQUIRED)

add_executable(pub_sub src/pub_sub.cpp)
ament_target_dependencies(
  pub_sub
  "rclcpp"
  "turtlesim"
  "rosidl_runtime_cpp"
  "geometry_msgs"
)
add_executable(server src/server.cpp)
ament_target_dependencies(
  server
  "rclcpp"
  "turtlesim"
  "base_interface"
  "geometry_msgs"
)
add_executable(client src/client.cpp)
ament_target_dependencies(
  client
  "rclcpp"
  "turtlesim"
  "base_interface"
  "geometry_msgs"
)

install(TARGETS 
  pub_sub
  server
  client
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
