import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from base_interface.msg import Turtle, TurtleArray
from base_interface.srv import CatchTurtle
from functools import partial
import math
                             
class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.declare_parameter("catch_closest_turtle_first", True)
        self.catch_closest_turtle_first_=self.get_parameter("catch_closest_turtle_first").value

        self.pose_=None
        self.turtle_to_catch_=None
        self.cmd_pub_=self.create_publisher(
            Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub_=self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        self.alive_turtles_sub_=self.create_subscription(
            TurtleArray, 'alive_turtles', self.alive_turtles_callback, 10)
        self.catch_turtle_client_=self.create_client(CatchTurtle, 'catch_turtle')
        self.control_loop_timer_ = self.create_timer(
            0.02, self.control_loop)  # 50 Hz 控制循环
    # pose_callback：接收乌龟的位姿信息，更新 self.pose_ 以供控制循环使用
    def pose_callback(self, pose: Pose):
        self.pose_ = pose
    # alive_turtles_callback：接收存活乌龟列表，更新 self.alive_turtles_ 以供控制循环使用
    def alive_turtles_callback(self, turtles: TurtleArray):
        if len(turtles.turtles)>0:
            if self.catch_closest_turtle_first_:
                closest_turtle=None
                min_turtle_distance=float('inf')
                # 找到最近的乌龟
                for turtle in turtles.turtles:
                    distance=(turtle.x-self.pose_.x)**2+(turtle.y-self.pose_.y)**2
                    if distance<min_turtle_distance or closest_turtle == None:
                        min_turtle_distance=distance
                        closest_turtle=turtle
                self.turtle_to_catch_ = closest_turtle
            else:
                self.turtle_to_catch_ = turtles.turtles[0]
    # control_loop：控制循环函数，根据当前位姿和目标点计算控制指令，发布到 /turtle1/cmd_vel 话题
    def control_loop(self):
        if self.pose_ ==None or self.turtle_to_catch_ is None:
            return  # 尚未收到位姿信息，等待下一次循环
        dist_x=self.turtle_to_catch_.x - self.pose_.x
        dist_y=self.turtle_to_catch_.y - self.pose_.y
        dist=math.sqrt(pow(dist_x,2)+pow(dist_y,2))
        cmd = Twist()
        if dist<0.5:
            self.get_logger().info('目标点已到达！')
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.catch_turtle_service(self.turtle_to_catch_.name)
            self.turtle_to_catch_=None
        else:
            cmd.linear.x = 2*dist  # 前进速度
            theta=math.atan2(dist_y,dist_x)-self.pose_.theta
            if theta>math.pi:
                theta-=2*math.pi
            elif theta<-math.pi:
                theta+=2*math.pi
            cmd.angular.z = 6*theta # 转向速度，目标是朝向正北（theta=3.14）

        # 发布控制指令
        self.cmd_pub_.publish(cmd)
    #调用catch_turtle 服务
    def catch_turtle_service(self,turtle_name):
        while not self.catch_turtle_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待 catch_turtle 服务...')
            return
        req=CatchTurtle.Request()
        req.name=turtle_name
        future=self.catch_turtle_client_.call_async(req)
        future.add_done_callback(partial(
            self.callback_catch_service,turtle_name=turtle_name))
    #catch_turtle回调函数
    def callback_catch_service(self,future,turtle_name):
        response=future.result()
        if response.success:
            self.get_logger().info(f'成功捕获乌龟{turtle_name}！')
        else:
            self.get_logger().error(f'捕获乌龟{turtle_name}失败！')

def main():
    rclpy.init()
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()