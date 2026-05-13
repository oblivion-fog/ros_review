import rclpy
from rclpy.node import Node
from base_interface.srv import Addint
                             
class AddIntsServerNode(Node):
    def __init__(self):
        super().__init__('addints_server')
        self.srv = self.create_service(Addint, 'addints', self.addints_callback)
        self.get_logger().info('AddInts service is ready.')

    def addints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Incoming request: a={request.a}, b={request.b} Response: sum={response.sum}')
        return response

def main():
    rclpy.init()
    node = AddIntsServerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()