import rclpy
# import sys
from rclpy.node import Node
from base_interface.srv import MultipyThree
import time


class MulThreeClientNode(Node):
    def __init__(self) -> None:
        super().__init__('multhree_client')
        self.cli = self.create_client(MultipyThree, 'multipy')

        # Wait for the service to be available
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

    def send_request(self, a: int, b: int, c: int) -> int:
        req = MultipyThree.Request()
        req.a = a
        req.b = b
        req.c = c

        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)

        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error(f'Service call failed for {a}x{b}x{c}: {e}')
            raise

        return int(response.result)


def main() -> None:
    rclpy.init()
    node = MulThreeClientNode()

    # 持续发送：循环重复 1..3 的所有组合，直到程序被停止
    # while rclpy.ok():
    for a in range(1, 4):
        for b in range(1, 4):
            for c in range(1, 4):
                result = node.send_request(a, b, c)
                node.get_logger().info(f'{a}x{b}x{c} = {result}')
                time.sleep(0.5)  # 每次请求之间等待 1 秒

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
