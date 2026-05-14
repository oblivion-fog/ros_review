from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # turtlesim：提供 /turtle1/pose 等话题，以及 turtlesim 内置的乌龟仿真环境
    turtle = Node(
        package="turtlesim",
        executable="turtlesim_node",
    )

    # exercise：测距服务端节点（订阅 /turtle1/pose，并提供名为 "distance" 的服务）
    # C++ 程序入口通常对应 exercise/src/server.cpp 里编译出来的可执行文件 "server"
    server = Node(
        package="exercise",
        executable="server",
    )

    # 同时启动：先有 turtlesim，再有 distance 服务对外响应
    return LaunchDescription([turtle, server])
