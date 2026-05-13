import rclpy
from rclpy.node import Node
from base_interface.msg import Student
                             
class StuPubNode(Node):
    def __init__(self):
        super().__init__('stu_pub')
        #创建一个发布者，发布Student类型的消息，主题名为'stu_info'，队列长度为10
        self.publisher_= self.create_publisher(Student,'stu_info',10)
        self.timer_ = self.create_timer(1,self.timer_callback)  
    def timer_callback(self):
        msg = Student()
        msg.name = '张三'
        msg.age = 20
        msg.height = 180.5
        self.publisher_.publish(msg)
        self.get_logger().info('发布了学生信息：name=%s,age=%d,height=%.2f' % (msg.name, msg.age, msg.height))


def main():
    rclpy.init()
    node = StuPubNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()