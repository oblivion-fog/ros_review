"""  
    需求：编写静态坐标变换程序，执行时传入两个坐标系的相对位姿关系以及父子级坐标系id，
         程序运行发布静态坐标变换。
    步骤：
        1.导包；
        2.判断终端传入的参数是否合法；
        3.初始化 ROS 客户端；
        4.定义节点类；
            4-1.创建静态坐标变换发布方；
            4-2.组织并发布消息。
        5.调用 spin 函数，并传入对象；
        6.释放资源。 

"""
import rclpy
from rclpy.node import Node
import sys
from geometry_msgs.msg import TransformStamped
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
import tf_transformations
import math
                             
class TfBroadcaster(Node):
    def __init__(self, argv):
        super().__init__('static_tf_broadcaster_py')
        #创建广播对象
        self.tf_broadcaster = StaticTransformBroadcaster(self)
        #组织并发布数据
        self.make_transforms(argv)
    
    def make_transforms(self,argv):
        ts = TransformStamped()
        #get_clock() 获取节点的时钟对象，now() 获取当前时间，to_msg() 将时间转换为消息格式
        ts.header.stamp = self.get_clock().now().to_msg()
        ts.header.frame_id = argv[7] #父级坐标系id
        ts.child_frame_id = argv[8] #子级坐标系id
        #组织坐标变换数据
        ts.transform.translation.x = float(argv[1])
        ts.transform.translation.y = float(argv[2])
        ts.transform.translation.z = float(argv[3])
        #将欧拉角转换为四元数
        qtn = tf_transformations.quaternion_from_euler(
            float(argv[4])*math.pi/180, float(argv[5])*math.pi/180, float(argv[6])*math.pi/180)
        ts.transform.rotation.x = qtn[0]
        ts.transform.rotation.y = qtn[1]
        ts.transform.rotation.z = qtn[2]
        ts.transform.rotation.w = qtn[3]
        #发布坐标变换
        self.tf_broadcaster.sendTransform(ts)

def main():
    argv = sys.argv
    if len(argv) != 9:
        print("Usage: static_tf_broadcaster_py.py <x> <y> <z> <roll> <pitch> <yaw> <parent_frame> <child_frame>")
        return

    rclpy.init()
    node = TfBroadcaster(argv)
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()