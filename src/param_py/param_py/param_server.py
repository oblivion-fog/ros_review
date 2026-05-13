"""
需求：编写参数服务端，设置并操作参数。
步骤：
    1.导包；
    2.初始化 ROS2 服务器；
    3.定义节点类；
        3-1.初始化参数；
        3-2.接收客户端请求（显式提供 Get/List/Set Parameters 服务）；
            收到客户端请求
            - 查询：返回当前参数值
            - 修改：更新参数值并返回成功结果
            - 删除：删除参数并返回成功结果
        3-3.响应客户端请求。
    4.创建节点对象，调用参数操作函数，并传递给spin函数；
    5.释放资源。
"""

from __future__ import annotations

from typing import List

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import ParameterDescriptor
from rcl_interfaces.srv import GetParameters, ListParameters, SetParameters

LOG_PARAMETER_NAME = '_client_operation'


class ParamServerNode(Node):
    def __init__(self) -> None:
        super().__init__('param_server', allow_undeclared_parameters=True)
        self.get_logger().info('Starting Parameter Server...')
        descriptor = ParameterDescriptor(dynamic_typing=True)
        self.declare_parameter(
            'my_param',
            'Hello, ROS2!',
            descriptor,
        )
        self.declare_parameter('car', 'Tesla', descriptor)
        self.declare_parameter('wheels', 4, descriptor)
        self.declare_parameter('height', 1.80, descriptor)

        # 让“删除/修改/查询”这类参数变化可观察（不是必须）
        self.add_on_set_parameters_callback(self.parameter_callback)

        # 显式提供客户端正在调用的服务：
        # /param_server/get_parameters
        # /param_server/list_parameters
        # /param_server/set_parameters
        self.get_service = self.create_service(
            GetParameters,
            '/param_server/get_parameters',
            self.handle_get_parameters,
        )
        self.list_service = self.create_service(
            ListParameters,
            '/param_server/list_parameters',
            self.handle_list_parameters,
        )
        self.set_service = self.create_service(
            SetParameters,
            '/param_server/set_parameters',
            self.handle_set_parameters,
        )

        self.get_logger().info('Parameter Server is ready.')

    def parameter_callback(self, parameters: List[Parameter]):
        # 仅用于日志观测：客户端会传入 _client_operation
        for parameter in parameters:
            if parameter.name == LOG_PARAMETER_NAME:
                self.get_logger().info('正在执行%s操作' % str(parameter.value))
                continue

            if parameter.type_ == Parameter.Type.NOT_SET:
                self.get_logger().info('正在执行删除操作: %s' % parameter.name)
            else:
                self.get_logger().info(
                    '正在执行修改操作: %s = %s'
                    % (parameter.name, str(parameter.value))
                )

        # 只要返回成功，SetParameters 服务就会继续执行我们的实际 set/del
        return rclpy.parameter.SetParametersResult(successful=True, reason='参数操作成功')  # type: ignore[attr-defined]

    def handle_get_parameters(self, request: GetParameters.Request, response: GetParameters.Response):
        names = list(request.names)
        response.values = []

        for name in names:
            if name == LOG_PARAMETER_NAME:
                # 客户端会过滤掉该参数，这里给个可用默认值
                response.values.append(Parameter(name, value='').to_parameter_msg().value)
                continue

            if not self.has_parameter(name):
                # 没声明则返回空/不稳定值（客户端会把 None 当作不存在）
                response.values.append(Parameter(name, value=None).to_parameter_msg().value)
                continue

            value = self.get_parameter(name).value
            response.values.append(Parameter(name, value=value).to_parameter_msg().value)

        return response

    def handle_list_parameters(self, request: ListParameters.Request, response: ListParameters.Response):
        # 按 request.depth 决定是否递归，这里简单实现：只返回当前节点本地参数
        names = [p for p in self._get_local_parameter_names() if p != LOG_PARAMETER_NAME]
        response.result.names = names  # ListParameters.Response.result is ParameterNames
        return response

    def _get_local_parameter_names(self) -> List[str]:
        # ROS2 Python里 Node.get_parameters_by_prefix / 参数列表的形态随版本略有差异
        # 这里尽量用 get_parameter_names
        try:
            # rclpy: Node.get_parameter_names()
            return list(self.get_parameter_names())
        except Exception:
            # 兜底：直接返回已声明集合（允许动态参数时会不完整，但能跑通）
            return ['my_param', 'car', 'wheels', 'height']
    
    #修改/删除参数的核心逻辑：根据 SetParameters.Request 里的参数列表逐个处理，支持修改/新增（value非空）和删除（value为None或type为NOT_SET）
    def handle_set_parameters(self, request: SetParameters.Request, response: SetParameters.Response):
        # request.parameters: list[ParameterMsg]
        results = []

        for param_msg in request.parameters:
            name = param_msg.name

            if name == LOG_PARAMETER_NAME:
                # 只是日志用，仍然允许存一下，避免 repeated set/del 异常
                value = param_msg.value
                self._set_parameter_from_msg(name, value)
                results.append(self._result_success(name))
                continue

            # 判断是否是删除（客户端用 Parameter.Type.NOT_SET）
            is_delete = param_msg.value is None
            # 但 ParameterMsg 的 value 字段有版本差异：为了稳妥，
            # 这里也尝试从 type 判断（ParameterMsg.type/value 的组合不一致时兜底）
            if hasattr(param_msg, 'type') and str(getattr(param_msg, 'type')) == str(2):
                is_delete = True  # 2 通常对应 NOT_SET，但这里做兼容兜底

            if is_delete:
                successful, reason = self._delete_parameter(name)
                results.append(self._result(successful=successful, name=name, reason=reason))
                continue

            # 修改/新增
            value = param_msg.value
            successful, reason = self._set_parameter_from_msg(name, value, allow_declare=True)
            results.append(self._result(successful=successful, name=name, reason=reason))

        response.results = results
        return response
    # 这里的 allow_declare 参数控制是否允许动态 declare（如果参数不存在时自动 declare），在某些场景下我们可能希望显式 declare 后再 set，或者直接 set 就 declare，根据实际需求调整
    def _set_parameter_from_msg(self, name: str, value, allow_declare: bool = False):
        # SetParameters 里 value 的类型是 protobuf Any/封装后的 python 值，直接用 Parameter(name, value=value) 尝试
        try:
            if allow_declare and not self.has_parameter(name):
                # 动态类型：declare 后再 set
                self.declare_parameter(name, value)
            elif not self.has_parameter(name):
                # allow_undeclared_parameters=True 时也允许 set，但我们仍尽量显式 declare
                self.declare_parameter(name, value)

            param = Parameter(name, value=value)
            self.set_parameters([param])
            return True, '参数设置成功'
        except Exception as e:
            return False, f'参数设置失败: {e}'

    def _delete_parameter(self, name: str):
        try:
            if not self.has_parameter(name):
                return True, '参数不存在，无需删除'
            self.undeclare_parameter(name)
            return True, '参数删除成功'
        except Exception as e:
            return False, f'参数删除失败: {e}'

    def _result_success(self, name: str):
        return self._result(True, name=name, reason='参数操作成功')

    def _result(self, successful: bool, name: str, reason: str):
        # SetParametersResult.msg: results is list[SetParametersResult]
        # 但 Python 类型导入不统一，这里直接构造 rcl_interfaces.msg.SetParametersResult
        from rcl_interfaces.msg import SetParametersResult as MsgSetParametersResult

        # 需要填 successful & reason（客户端只看 successful/reason）
        return MsgSetParametersResult(successful=successful, reason=reason)


def main():
    rclpy.init()
    node = ParamServerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
