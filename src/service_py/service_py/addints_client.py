import rclpy
import sys
from rclpy.node import Node
from base_interface.srv import Addint

                             
class AddIntsClientNode(Node):
    def __init__(self):
        super().__init__('addints_client')
        self.cli = self.create_client(Addint, 'addints')
        # Wait for the service to be available
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
    #only send the request
    def send_request(self):
        self.req = Addint.Request()
        self.req.a = int(sys.argv[1])
        self.req.b = int(sys.argv[2])
        #call the service asynchronously and wait for the result
        self.future = self.cli.call_async(self.req)   
        return self.future.result()

def main():
    if len(sys.argv) != 3:
        node.get_logger().info('Usage: addints_client a b')
        return
    
    rclpy.init()
    node = AddIntsClientNode()
    response = node.send_request()
    #deal with the response
    #spin until the future is complete, then get the result
    rclpy.spin_until_future_complete(node, node.future)
    try:
        response = node.future.result()
    except Exception as e:
        node.get_logger().error(f'Service call failed: {e}')
    else:
        node.get_logger().info(f'Sum: {response.sum}')
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()