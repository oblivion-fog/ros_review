"""tf_listener 示例节点。

此模块实现一个简单的 tf2 监听器节点，演示如何让一个乌龟（child）跟随另一个乌龟（parent）。
节点通过参数配置跟随目标、缩放系数、停止距离以及目标偏移，并发布速度命令到 `/<child_name>/cmd_vel`。
"""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import math
from tf2_ros import TransformException, TransformListener, Buffer
from geometry_msgs.msg import Twist
                             
class TfListener(Node):
    """tf 监听器节点类。

    参数通过 ROS 参数服务器声明并读取：
    - `parent_name`: 要跟随的目标帧名称（默认 'turtle1'）
    - `child_name`: 执行运动的乌龟帧名称（默认 'turtle2'）
    - `linear_scale`: 线速度缩放系数
    - `angular_scale`: 角速度缩放系数
    - `stop_distance`: 距离低于该值时停止移动
    - `target_offset_x`, `target_offset_y`: 目标在 parent_name 坐标系中的偏移

    该类创建 tf2 缓冲区及监听器、一个发布器用于发布 `Twist`，并创建定时器定期查询变换并发布速度。
    """
    def __init__(self):
        super().__init__('tf_listener')
        # parent_name 是要跟随的目标，child_name 是执行运动的乌龟。
        self.declare_parameter('parent_name', 'turtle1')
        self.declare_parameter('child_name', 'turtle2')
        self.parent_name = self.get_parameter('parent_name').get_parameter_value().string_value
        self.child_name = self.get_parameter('child_name').get_parameter_value().string_value
        self.declare_parameter('linear_scale', 1.5)
        self.declare_parameter('angular_scale', 4.0)
        self.declare_parameter('stop_distance', 0.05)
        self.declare_parameter('target_offset_x', 0.0)
        self.declare_parameter('target_offset_y', 0.0)
        self.linear_scale = self.get_parameter('linear_scale').get_parameter_value().double_value
        self.angular_scale = self.get_parameter('angular_scale').get_parameter_value().double_value
        self.stop_distance = self.get_parameter('stop_distance').get_parameter_value().double_value
        self.target_offset_x = self.get_parameter(
            'target_offset_x').get_parameter_value().double_value
        self.target_offset_y = self.get_parameter(
            'target_offset_y').get_parameter_value().double_value
        # 创建 tf2 缓冲区和监听器
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        # 创建发布器
        self.cmd_vel_pub = self.create_publisher(Twist, f'/{self.child_name}/cmd_vel', 10)
        # 创建定时器，提高控制频率可以让跟随更平滑。
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info(
            f'{self.child_name} following {self.parent_name} '
            f'at offset ({self.target_offset_x:.2f}, {self.target_offset_y:.2f})')

    def timer_callback(self):
        """定时回调：查询目标到当前乌龟的变换并发布速度命令。

        - 查询从 `child_name` 到 `parent_name` 的变换（即在 child 坐标系下的 parent 位姿），
        - 根据偏移计算目标点在 child 坐标系下的位置，计算距离与角度，生成并发布 `Twist`。
        """
        try:
            # 查询“目标乌龟在当前乌龟坐标系下”的位置。
            ts = self.tf_buffer.lookup_transform(
                self.child_name,
                self.parent_name,
                rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().debug(
                f'Could not transform {self.child_name} -> {self.parent_name}: {ex}')
            return

        parent_x = ts.transform.translation.x
        parent_y = ts.transform.translation.y
        # 提取四元数并计算父框架的偏航角（yaw）
        rotation = ts.transform.rotation
        parent_yaw = math.atan2(
            2.0 * (rotation.w * rotation.z + rotation.x * rotation.y),
            1.0 - 2.0 * (rotation.y ** 2 + rotation.z ** 2))

        # target_offset_* 定义在 parent_name 坐标系中：
        # x 为前后，y 为左右。这里把偏移点转换到 child_name 坐标系中。
        x = (
            parent_x
            + math.cos(parent_yaw) * self.target_offset_x
            - math.sin(parent_yaw) * self.target_offset_y)
        y = (
            parent_y
            + math.sin(parent_yaw) * self.target_offset_x
            + math.cos(parent_yaw) * self.target_offset_y)
        distance = math.sqrt(x ** 2 + y ** 2)

        twist = Twist()
        if distance > self.stop_distance:
            twist.angular.z = self.angular_scale * math.atan2(y, x)
            twist.linear.x = self.linear_scale * distance

        self.cmd_vel_pub.publish(twist)

def main():
    """程序入口：初始化 ROS、创建节点并开始自旋。

    支持通过 Ctrl-C 或外部关机异常干净地退出并销毁节点。
    """
    rclpy.init()
    node = TfListener()
    try:
        rclpy.spin(node)
    #keyboardinterrupt 和外部关机异常都能正常退出
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
