import rclpy
from rclpy.node import Node
from functools import partial
import random
from turtlesim.srv import Spawn
from base_interface.msg import Turtle, TurtleArray
from base_interface.srv import CatchTurtle
from turtlesim.srv import Kill
                             
class TurtleSpawnerNode(Node):
    def __init__(self):
        super().__init__('turtle_spawner')
        #设置参数：乌龟名字前缀和生成频率
        self.declare_parameter('turtle_name_prefix', 't')
        self.turtle_name_prefix_ = self.get_parameter('turtle_name_prefix').value
        self.declare_parameter("turtle_frequency", 0.8)  # 每秒生成的乌龟数量
        self.turtle_frequency_ = self.get_parameter("turtle_frequency").value

        self.turtle_count_ = 0
        self.alive_turtles_=[]
        self.alive_turtles_pub_ = self.create_publisher(TurtleArray, 'alive_turtles', 10)
        self.spawn_client_ = self.create_client(Spawn, '/spawn')
        self.kill_client_ = self.create_client(Kill, '/kill')

        self.catch_turtle_service_ = self.create_service(
            CatchTurtle, 'catch_turtle', self.catch_turtle_callback)
        self.spawn_turtle_timer_ = self.create_timer(
            self.turtle_frequency_, self.spawn_turtle_timer_callback)  # 每隔 1 秒尝试调用一次 spawn 服务
    # catch_turtle_callback：捕获乌龟的服务回调函数，接收要捕获的乌龟名字，调用 /kill 服务删除该乌龟，并在响应中返回捕获结果
    def catch_turtle_callback(self, request, response):
        turtle_name=request.name
        # 调用 /kill 服务删除被捕获的乌龟
        while not self.kill_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待 /kill 服务...')
        kill_req=Kill.Request()
        kill_req.name=turtle_name
        #异步调用 /kill 服务，并在回调函数中处理响应，实现捕获乌龟后更新存活乌龟列表并发布更新后的列表
        future=self.kill_client_.call_async(kill_req)
        future.add_done_callback(partial(self.callback_call_kill_service,turtle_name=turtle_name))
        response.success=True
        return response

    # spawn_new_turtle：生成新的乌龟，名字为 t1、t2、t3...，位置随机分布在 turtlesim 的 11x11 范围内，朝向随机
    def spawn_new_turtle(self):
        self.turtle_count_ += 1
        name = f"{self.turtle_name_prefix_}{self.turtle_count_}"
        x = random.uniform(0.1, 10.0)
        y = random.uniform(0.1, 10.0)
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
        #异步调用 /spawn 服务，并在回调函数中处理响应，实现生成乌龟后更新存活乌龟列表并发布更新后的列表
        #future 是一个 Future 对象，表示异步调用的结果，add_done_callback 方法用于指定当 Future 完成时要调用的回调函数，这里使用 partial 将请求参数传递给回调函数
        #call_async 方法用于异步调用服务，返回一个 Future 对象，表示服务调用的结果
        future = self.spawn_client_.call_async(req)
        future.add_done_callback(partial(self.callback_call_spawn_service,request=req))
    
    #生成乌龟的回调函数：接收 /spawn 服务的响应
    #判断是否成功生成乌龟，如果成功则将新乌龟添加到 alive_turtles_ 列表并发布更新后的列表
    def callback_call_spawn_service(self, future,request):
        response=future.result()
        if response.name != "":
            self.get_logger().info(f"成功生成乌龟 '{response.name}'！")
            # 将新生成的乌龟添加到 alive_turtles_pub_ 发布的消息中
            turtle = Turtle()
            turtle.name = response.name
            turtle.x = request.x
            turtle.y = request.y
            turtle.theta = request.theta
            self.alive_turtles_.append(turtle) 
            self.pub_alive_turtles() # 发布更新后的乌龟列表
        else:
            self.get_logger().error('调用 /spawn 服务失败')
    # callback_call_kill_service：调用 /kill 服务的回调函数，参数为被捕获乌龟的名字，用于从 alive_turtles_ 列表中删除被捕获的乌龟并发布更新后的列表
    def callback_call_kill_service(self, future, turtle_name):
        for(i,turtle) in enumerate(self.alive_turtles_):
            if turtle.name==turtle_name:
                del self.alive_turtles_[i] 
                self.pub_alive_turtles()
                break

def main():
    rclpy.init()
    node = TurtleSpawnerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()