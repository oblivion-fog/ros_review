import rclpy
from rclpy.node import Node
from base_interface.srv import MultipyThree
                             
class MultipyThreeServerNode(Node):
    def __init__(self):
        super().__init__('multhree_server')
        self.srv = self.create_service(MultipyThree, 'multipy', self.multipythree_callback)
        self.get_logger().info('MultipyThree service is ready.')

    def multipythree_callback(self, request, response):
        response.result = request.a * request.b * request.c
        self.get_logger().info(f'Incoming request: a={request.a}, b={request.b}, c={request.c} Response: result={response.result}')
        return response

def main():
    rclpy.init()
    node = MultipyThreeServerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()