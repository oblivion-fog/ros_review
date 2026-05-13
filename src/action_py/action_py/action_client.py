import rclpy
import sys
from rclpy.node import Node
from base_interface.action import Progress
from rclpy.action import ActionClient
# import time
                             
class ActionClientNode(Node):
    def __init__(self):
        super().__init__('action_client')
        self._action_client = ActionClient(self, Progress, 'get_sum')
    def send_goal(self, num):
        # 3-1.等待 Action Server 可用。
        self._action_client.wait_for_server()
        # 3-2.发送请求；
        goal_msg = Progress.Goal()
        goal_msg.num = num
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        # 3-3.处理目标发送后的反馈；
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('请求被拒绝')
            rclpy.shutdown()
            return

        self.get_logger().info('请求被接收，开始执行任务！')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    # 3-5.处理最终响应。
    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('最终计算结果：sum = %d' % result.sum)
        # 5.释放资源。
        rclpy.shutdown()

    # 3-4.处理连续反馈；
    def feedback_callback(self, feedback_msg):
        feedback = (int)(feedback_msg.feedback.progress * 100)
        self.get_logger().info('当前进度: %d%%' % feedback)
    
def main():
    if len(sys.argv) != 2:
        print("请提供一个整数作为目标值！")
        return
    rclpy.init()
    node = ActionClientNode()
    node.send_goal(int(sys.argv[1]))  # 发送一个目标值为 10 的目标
    rclpy.spin(node)
    # rclpy.shutdown()

if __name__ == '__main__':
    main()