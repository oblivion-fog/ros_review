from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    # 1) 创建两个 turtlesim_node 节点
    #    - t1：默认 namespace（/turtle1/...）
    #    - t2：指定 namespace="t2"（/t2/turtle1/...），用于区分第二只乌龟
    t1 = Node(package="turtlesim", executable="turtlesim_node")
    t2 = Node(package="turtlesim", executable="turtlesim_node", namespace="t2")

    # 2) 让第二只乌龟掉头（rotate_absolute action）
    #    使用 turtlesim 内置 action：/t2/turtle1/rotate_absolute
    #    掉头角度设置为 3.14（弧度）
    rotate = ExecuteProcess(
        cmd=[
            "ros2 action send_goal /t2/turtle1/rotate_absolute turtlesim/action/RotateAbsolute \"{'theta': 3.14}\""
        ],
        output="both",
        shell=True,
    )

    # 3) 自实现的订阅发布实现
    #    exercise/src/pub_sub.cpp 通常负责订阅/发布某些话题（此处通过 Node 直接启动可执行文件）
    pub_sub = Node(package="exercise", executable="pub_sub")

    # 4) 旋转 action 发起后，等待 rotate 进程退出，再启动 pub_sub
    #    这样能保证 pub_sub 启动时 t2 的朝向变化已发生/或接近完成（取决于 turtlesim action 时长）
    rotate_exit_event = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=rotate,
            on_exit=pub_sub,
        )
    )

    return LaunchDescription([t1, t2, rotate, rotate_exit_event])
