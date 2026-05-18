import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from turtlesim.msg import Pose
import tf_transformations
                             
class TfBroadcaster(Node):
    def __init__(self):
        super().__init__('tf_broadcaster')
        #定义参数
        self.declare_parameter('turtle_name', 't1')
        self.turtle_name = self.get_parameter('turtle_name').get_parameter_value().string_value
        #创建动态坐标变换发布器
        self.tf_broadcaster = TransformBroadcaster(self)
        #订阅乌龟位姿
        self.subscription = self.create_subscription(
            Pose,
            f'/{self.turtle_name}/pose',
            self.pose_callback,
            10)
        self.subscription  # prevent unused variable warning
    def pose_callback(self, msg):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = self.turtle_name
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0
        q = tf_transformations.quaternion_from_euler(0, 0, msg.theta)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        self.tf_broadcaster.sendTransform(t)


def main():
    rclpy.init()
    node = TfBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()
