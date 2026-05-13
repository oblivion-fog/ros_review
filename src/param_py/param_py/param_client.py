"""  
    需求：编写参数客户端
    步骤：
        1.导包；
        2.初始化 ROS2 客户端；
        3.定义节点类；
            3-1.等待参数服务器；
            3-2.发送请求
             1.输入1 查询参数；
             2.输入2 修改参数，输入要修改参数名称和参数值；
             3.输入3 删除参数，输入要删除的参数名称。
             4.输入4 查询所有参数：参数名词+参数值；
             5.输入0 退出程序。
            
        4.创建节点对象，调用参数操作函数，并传递给spin函数；
        5.释放资源。

"""

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.parameter import parameter_value_to_python
from rcl_interfaces.srv import GetParameters
from rcl_interfaces.srv import ListParameters
from rcl_interfaces.srv import SetParameters

LOG_PARAMETER_NAME = '_client_operation'
                             
class ParamClientNode(Node):
    def __init__(self):
        super().__init__('param_client')
        self.get_client = self.create_client(
            GetParameters,
            '/param_server/get_parameters'
        )
        self.list_client = self.create_client(
            ListParameters,
            '/param_server/list_parameters'
        )
        self.set_client = self.create_client(
            SetParameters,
            '/param_server/set_parameters'
        )

    # 3-1.等待参数服务器；
    def wait_for_param_server(self):
        while (
            not self.get_client.wait_for_service(timeout_sec=1.0) or
            not self.list_client.wait_for_service(timeout_sec=1.0) or
            not self.set_client.wait_for_service(timeout_sec=1.0)
        ):
            self.get_logger().info('等待参数服务器...')
        self.get_logger().info('参数服务器已连接！')

    # 3-2.循环发送查询、修改、删除参数请求。
    def send_request(self):
        self.wait_for_param_server()

        while rclpy.ok():
            print('\n请选择参数操作：')
            print('1. 查询参数')
            print('2. 修改参数')
            print('3. 删除参数')
            print('4. 查询全部参数')
            print('0. 退出客户端')
            choice = input('请输入操作编号: ').strip()

            if choice == '1':
                name = input('请输入要查询的参数名称: ').strip()
                self.query_parameter(name)
            elif choice == '2':
                name = input('请输入要修改的参数名称: ').strip()
                value_text = input('请输入新的参数值: ').strip()
                self.set_parameter(name, self.parse_value(value_text))
            elif choice == '3':
                name = input('请输入要删除的参数名称: ').strip()
                self.delete_parameter(name)
            elif choice == '4':
                self.query_all_parameters()
            elif choice == '0':
                self.get_logger().info('客户端退出')
                break
            else:
                self.get_logger().error('无效操作编号，请输入 0、1、2、3 或 4')

    def query_parameter(self, name):
        self.notify_server_operation('查询')
        request = GetParameters.Request()
        request.names = [name]
        future = self.get_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        response = future.result()
        value = parameter_value_to_python(response.values[0])
        if value is None:
            self.get_logger().info('参数 %s 不存在' % name)
        else:
            self.get_logger().info('查询结果: %s = %s' % (name, str(value)))

    def query_all_parameters(self):
        self.notify_server_operation('查询全部参数')
        list_request = ListParameters.Request()
        list_request.depth = ListParameters.Request.DEPTH_RECURSIVE
        list_future = self.list_client.call_async(list_request)
        rclpy.spin_until_future_complete(self, list_future)

        names = [
            name for name in list_future.result().result.names
            if name != LOG_PARAMETER_NAME
        ]
        if not names:
            self.get_logger().info('当前没有参数')
            return

        get_request = GetParameters.Request()
        get_request.names = names
        get_future = self.get_client.call_async(get_request)
        rclpy.spin_until_future_complete(self, get_future)

        self.get_logger().info('全部参数如下：')
        for name, parameter_value in zip(names, get_future.result().values):
            value = parameter_value_to_python(parameter_value)
            self.get_logger().info('%s    %s' % (name, str(value)))

    def set_parameter(self, name, value):
        parameter = Parameter(name, value=value)
        self.call_set_parameters(parameter, '修改')

    def delete_parameter(self, name):
        parameter = Parameter(name, Parameter.Type.NOT_SET)
        self.call_set_parameters(parameter, '删除')

    def call_set_parameters(self, parameter, operation_name):
        request = SetParameters.Request()
        #将参数转换成 ParameterMsg 格式，并放入 request.parameters 列表中，发送给参数服务器
        request.parameters = [parameter.to_parameter_msg()]
        future = self.set_client.call_async(request)
        #等待服务端处理完成后返回结果，才能继续执行后续逻辑（比如打印成功/失败信息）
        rclpy.spin_until_future_complete(self, future)

        result = future.result().results[0]
        if result.successful:
            self.get_logger().info('%s参数成功: %s' % (operation_name, parameter.name))
        else:
            self.get_logger().error(
                '%s参数失败: %s，原因: %s' %
                (operation_name, parameter.name, result.reason)
            )
    # 将用户输入的字符串解析成合适的参数值类型，支持 bool、int、float 和字符串，方便用户直接输入参数值
    def parse_value(self, value_text):
        lower_value = value_text.lower()
        if lower_value == 'true':
            return True
        if lower_value == 'false':
            return False

        try:
            return int(value_text)
        except ValueError:
            pass

        try:
            return float(value_text)
        except ValueError:
            return value_text
    # 通过设置一个特殊参数 _client_operation 来通知服务器当前正在执行的操作（查询/修改/删除）
    # 服务器可以根据这个参数进行日志记录或其他处理，这样在服务器端就能看到客户端的操作意图，方便调试和监控
    def notify_server_operation(self, operation_name):
        parameter = Parameter(LOG_PARAMETER_NAME, value=operation_name)
        request = SetParameters.Request()
        request.parameters = [parameter.to_parameter_msg()]
        future = self.set_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

def main():
    rclpy.init()
    node = ParamClientNode()
    node.send_request()

    rclpy.shutdown()

if __name__ == '__main__':
    main()
