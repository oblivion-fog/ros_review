import rclpy
from rclpy.node import Node
from functools import partial
import random
from turtlesim.srv import Spawn
from base_interface.msg import Turtle, TurtleArray
                             
class TurtleSpawnerNode(Node):
    def __init__(self):
        super().__init__('turtle_spawner')
        self.turtle_name_prefix_ = "t"
        self.turtle_count_ = 0
        self.alive_turtles_=[]
        self.alive_turtles_pub_ = self.create_publisher(TurtleArray, 'alive_turtles', 10)
        self.spawn_client_ = self.create_client(Spawn, '/spawn')
        self.spawn_turtle_timer_ = self.create_timer(1.0, self.spawn_turtle_timer_callback)  # 每隔 1 秒尝试调用一次 spawn 服务
    # spawn_new_turtle：生成新的乌龟，名字为 t1、t2、t3...，位置随机分布在 turtlesim 的 11x11 范围内，朝向随机
    def spawn_new_turtle(self):
        self.turtle_count_ += 1
        name = f"{self.turtle_name_prefix_}{self.turtle_count_}"
        x = random.uniform(0.1, 11.0)
        y = random.uniform(0.1, 11.0)
        theta = random.uniform(0.0, 6.28)
        self.call_spawn_service(x, y,theta, name)
    # pub_alive_turtles：发布当前存活的乌龟列表，消息类型为 base_interface/msg/TurtleArray
    def pub_alive_turtles(self):
        msg=TurtleArray()
        msg.turtles=self.alive_turtles_
        self.alive_turtles_pub_.publish(msg)
    
    # spawn_turtle_timer_callback：定时器回调函数，调用 spawn_new_turtle 生成新的乌龟
    def spawn_turtle_timer_callback(self):
        self.spawn_new_turtle()
    
    # call_spawn_service：调用 /spawn 服务生成新的乌龟，参数为位置和名字
    def call_spawn_service(self, x, y, theta, name):
        while not self.spawn_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待 /spawn 服务...')
        req = Spawn.Request()
        req.x = x
        req.y = y
        req.theta = theta
        req.name = name
        future = self.spawn_client_.call_async(req)
        future.add_done_callback(partial(self.callback_call_spawn_service,request=req))

    def callback_call_spawn_service(self, future,request):
        response=future.result()
        if response.name != "":
            self.get_logger().info(f"成功生成乌龟 '{response.name}'！")
            # 将新生成的乌龟添加到 alive_turtles_pub_ 发布的消息中
            turtle = Turtle()
            turtle.name = response.name
            turtle.x = response.x
            turtle.y = response.y
            turtle.theta = response.theta
            self.alive_turtles_.append(turtle) 
            self.pub_alive_turtles() # 发布更新后的乌龟列表
        else:
            self.get_logger().error('调用 /spawn 服务失败')

def main():
    rclpy.init()
    node = TurtleSpawnerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()