cmake_minimum_required(VERSION 3.8)
project(base_interface)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Student.msg"
  "msg/Turtle.msg"
  "msg/TurtleArray.msg"
  "srv/Addint.srv"
  "srv/MultipyThree.srv"
  "srv/Distance.srv"
  "action/Progress.action"
  
)


ament_package()
