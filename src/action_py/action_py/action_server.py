import rclpy
from rclpy.node import Node
from base_interface.action import Progress
from rclpy.action import ActionServer, GoalResponse, CancelResponse
import time
                             
class ActionServerNode(Node):
    def __init__(self):
        super().__init__('action_server')
        #创建一个名为 get_sum 的 Action Server，使用 Progress 作为接口，并指定 execute_callback 作为执行回调函数
        self._action_server = ActionServer(
            self,
            Progress,
            'get_sum',
            self.execute_callback,
            goal_callback=self.action_goal_callback
            )
        self.get_logger().info('Action Server is ready.')
    #遇到非法目标值时，拒绝请求；对于合法目标值，接受请求并开始执行任务。
    def action_goal_callback(self, goal_request):
        self.get_logger().info('收到目标请求: num = %d' % goal_request.num)
        if goal_request.num <= 0:
            self.get_logger().info('拒绝请求: num 必须大于 0')
            return rclpy.action.GoalResponse.REJECT
        self.get_logger().info('接受请求: num = %d' % goal_request.num)
        return GoalResponse.ACCEPT
    

    async def execute_callback(self, goal_handle):
        self.get_logger().info("正在执行任务...")
        #生成连续反馈并发布
        feedback_msg = Progress.Feedback()

        sum = 0
        for i in range(1, goal_handle.request.num + 1):
            sum += i
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.sum = sum
                self.get_logger().info('任务取消')
                return result
            feedback_msg.progress = i / goal_handle.request.num
            self.get_logger().info('连续反馈: %.2f' % feedback_msg.progress)
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.5)  # 模拟计算过程中的延迟

        # 3-3.生成最终响应。
        goal_handle.succeed()
        result = Progress.Result()
        result.sum = sum
        self.get_logger().info('最终结果: sum = %d' % result.sum)
        self.get_logger().info('任务完成！')

        return result


def main():
    rclpy.init()
    node = ActionServerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
