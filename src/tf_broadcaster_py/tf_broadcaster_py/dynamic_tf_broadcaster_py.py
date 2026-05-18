"""  
  需求：编写动态坐标变换程序，启动 turtlesim_node 以及 turtle_teleop_key 后，该程序可以发布
       乌龟坐标系到窗口坐标系的坐标变换，并且键盘控制乌龟运动时，乌龟坐标系与窗口坐标系的相对关系
       也会实时更新。

  步骤：
    1.导包；
    2.初始化 ROS 客户端；
    3.定义节点类；
      3-1.创建动态坐标变换发布方；
      3-2.创建乌龟位姿订阅方；
      3-3.根据订阅到的乌龟位姿生成坐标帧并广播。
    4.调用 spin 函数，并传入对象；
    5.释放资源。
"""
# 1.导包；
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
import tf_transformations
from turtlesim.msg import Pose

class DynamicTfBoardcasterNode(Node):
    def __init__(self):
        super().__init__('dynamic_tf_broadcaster_py')
        # 3-1.创建动态坐标变换发布方；
        self.tf_broadcaster = TransformBroadcaster(self)
        # 3-2.创建乌龟位姿订阅方；
        self.create_subscription(Pose, 'turtle1/pose', self.pose_callback, 10)
    # 3-3.根据订阅到的乌龟位姿生成坐标帧并广播。
    def pose_callback(self, msg):
        ts = TransformStamped()
        ts.header.stamp = self.get_clock().now().to_msg()
        ts.header.frame_id = 'world'
        ts.child_frame_id = 'turtle1'
        #组织坐标变换数据
        ts.transform.translation.x = msg.x
        ts.transform.translation.y = msg.y
        ts.transform.translation.z = 0.0
        #将欧拉角转换为四元数
        qtn = tf_transformations.quaternion_from_euler(0, 0, msg.theta)
        ts.transform.rotation.x = qtn[0]
        ts.transform.rotation.y = qtn[1]
        ts.transform.rotation.z = qtn[2]
        ts.transform.rotation.w = qtn[3]
        #发送坐标变换
        self.tf_broadcaster.sendTransform(ts)
    


def main():
    rclpy.init()
    node = DynamicTfBoardcasterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()