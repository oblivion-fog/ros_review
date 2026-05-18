import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer
from rclpy.time import Time        
class TfListener(Node):
    def __init__(self):
        super().__init__('tf_listener')
        #缓存区和监听器
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0, self.timer_callback)
    def timer_callback(self):
        if self.tf_buffer.can_transform('camera', 'laser', Time()):
            transform = self.tf_buffer.lookup_transform('camera', 'laser', Time())
            self.get_logger().info(
                f"Translation: parent frame: %s, child frame: %s, translation: (%.2f, %.2f, %.2f)" % 
                (transform.header.frame_id, 
                 transform.child_frame_id, 
                 transform.transform.translation.x, 
                 transform.transform.translation.y,
                 transform.transform.translation.z))
        else:
            self.get_logger().info("Transform not available")

def main():
    rclpy.init()
    node = TfListener()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()