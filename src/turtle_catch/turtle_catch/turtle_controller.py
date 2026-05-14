import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
                             
class TurtleControllerNode(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.pose_=None
        self.targle_x=9.5
        self.targle_y=1.0
        self.cmd_pub_=self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub_=self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.control_loop_timer_ = self.create_timer(0.02, self.control_loop)  # 50 Hz 控制循环
    # pose_callback：接收乌龟的位姿信息，更新 self.pose_ 以供控制循环使用
    def pose_callback(self, pose: Pose):
        self.pose_ = pose
       
    def control_loop(self):
        if self.pose_ ==None:
            return  # 尚未收到位姿信息，等待下一次循环
        dist_x=self.targle_x - self.pose_.x
        dist_y=self.targle_y - self.pose_.y
        dist=math.sqrt(pow(dist_x,2)+pow(dist_y,2))
        cmd = Twist()
        if dist<0.5:
            self.get_logger().info('目标点已到达！')
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
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

def main():
    rclpy.init()
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()