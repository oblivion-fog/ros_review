import rclpy
from rclpy.node import Node
from base_interface.msg import Student
                             
class StuSubNode(Node):
    def __init__(self):
        super().__init__('stu_sub')
        self.subscription_ = self.create_subscription(
            Student,
            'stu_info',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info('接收到学生信息：name=%s,age=%d,height=%.2f' % (msg.name, msg.age, msg.height))

def main():
    rclpy.init()
    node = StuSubNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()