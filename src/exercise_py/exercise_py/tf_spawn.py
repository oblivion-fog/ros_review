import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
                             
class TfSpawnNode(Node):
    def __init__(self):
        super().__init__('tf_spawn')
        #定义参数
        self.declare_parameter('x', 2.0)
        self.declare_parameter('y', 2.0)
        self.declare_parameter('theta', 0.0)
        self.declare_parameter('turtle_name', 't2')
        self.x = self.get_parameter('x').get_parameter_value().double_value
        self.y = self.get_parameter('y').get_parameter_value().double_value
        self.theta = self.get_parameter('theta').get_parameter_value().double_value
        self.name = self.get_parameter('turtle_name').get_parameter_value().string_value
        #创建客户端
        self.client=self.create_client(Spawn,'/spawn')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
    #组织并发布数据
    def send_request(self):
        request=Spawn.Request()
        request.x=self.x
        request.y=self.y
        request.theta=self.theta
        request.name=self.name
        #发送数据
        self.future=self.client.call_async(request)


def main():
    rclpy.init()
    #创建对象并调用服务
    node = TfSpawnNode()
    node.send_request()
    #处理响应
    rclpy.spin_until_future_complete(node, node.future)
    try:
        response = node.future.result()
    except Exception as e:
        node.get_logger().info('Service call failed %r' % (e,))
    else:
        if len(response.name)==0:
            node.get_logger().info('Failed to spawn turtle')
        else:
            node.get_logger().info('Spawned a turtle named: %s' % response.name)
    # rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()