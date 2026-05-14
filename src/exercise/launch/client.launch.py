from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    # 目标点坐标（spawn 一只新的 turtlesim 乌龟作为目标）
    x = 9.5
    y = 1.0
    theta = 0.0

    # 目标点乌龟的名字（会作为 turtlesim_node 的 namespace 使用）
    name = "t2"

    # 生成新的乌龟（通过调用 turtlesim 的 /spawn 服务创建）
    # 注意：此处使用 ExecuteProcess 直接 shell 调用 ros2 service call。
    spawn = ExecuteProcess(
        cmd=[
            "ros2 service call /spawn turtlesim/srv/Spawn \"{'x': "
            + str(x)
            + ",'y': "
            + str(y)
            + ",'theta': "
            + str(theta)
            + ",'name': '"
            + name
            + "'}\""
        ],
        # output="both",
        shell=True,
    )

    # 创建客户端节点：向本包的测距服务发起请求
    # client.cpp 期望参数顺序为：x y theta
    client = Node(
        package="exercise",
        executable="client",
        arguments=[str(x), str(y), str(theta)],
    )

    # 同时启动：先生成目标乌龟，再启动 client 发送请求
    return LaunchDescription([spawn, client])
