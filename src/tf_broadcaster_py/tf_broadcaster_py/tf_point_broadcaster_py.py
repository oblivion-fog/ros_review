import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
                             
class TfPointBroadcasterNode(Node):
    def __init__(self):
        super().__init__('tf_point_broadcaster_py')
        self.point_pub_=self.create_publisher(PointStamped,'point',10)
        self.x=0.1
        self.timer=self.create_timer(0.5,self.timer_callback)
    def timer_callback(self):
        point_msg=PointStamped()
        point_msg.header.stamp=self.get_clock().now().to_msg()
        point_msg.header.frame_id='laser'
        self.x+=0.05
        point_msg.point.x=self.x
        point_msg.point.y=0.2
        point_msg.point.z=0.3
        self.point_pub_.publish(point_msg)


def main():
    rclpy.init()
    node = TfPointBroadcasterNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()