import rclpy
from rclpy.node import Node
import math
from tf2_ros import TransformListener, Buffer
# from tf2_ros import 
from geometry_msgs.msg import Twist
                             
class TfListener(Node):
    def __init__(self):
        super().__init__('tf_listener')
        #定义参数
        self.declare_parameter('parent_name', 'turtle1')
        self.declare_parameter('child_name', 'turtle2')
        self.parent_name = self.get_parameter('parent_name').get_parameter_value().string_value
        self.child_name = self.get_parameter('child_name').get_parameter_value().string_value
        #创建tf2缓冲区和监听器
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        #创建发布器
        self.cmd_vel_pub = self.create_publisher(Twist, f'/{self.child_name}/cmd_vel', 10)
        #创建定时器
        self.timer = self.create_timer(1.0, self.timer_callback)
    def timer_callback(self):
        if self.tf_buffer.can_transform(self.parent_name, self.child_name, rclpy.time.Time()):
            #查询坐标变换
            ts=self.tf_buffer.lookup_transform(
                self.parent_name, self.child_name, rclpy.time.Time())
            #计算控制命令
            twist = Twist()
            scale_rotation = 1.0
            twist.angular.z = scale_rotation * math.atan2(
                ts.transform.translation.y, ts.transform.translation.x)
            scale_forward = 0.5
            twist.linear.x = scale_forward * math.sqrt(
                ts.transform.translation.x ** 2 + 
                ts.transform.translation.y ** 2)
            #发布控制命令
            self.cmd_vel_pub.publish(twist)

def main():
    rclpy.init()
    node = TfListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()