#include "rclcpp/rclcpp.hpp"
#include "base_interface/srv/distance.hpp"
#include "turtlesim/srv/spawn.hpp"

using namespace std::chrono_literals;

// 计算距离客户端：连接到名为 "distance" 的服务，读取命令行参数 x/y/theta 发送请求，等待响应并打印结果。
// 说明：本客户端主要用到 base_interface/srv/Distance.srv 的 x/y（theta 作为参数透传给服务端）。

using DistanceSrv = base_interface::srv::Distance;

// 1) 节点类：继承 rclcpp::Node
class ExeDistanceClient : public rclcpp::Node {
public:
  // 2) 构造函数：初始化节点并创建 client
  ExeDistanceClient()
  : Node("exe_distance_client") {
    // 3-1) 创建客户端：连接服务名 "distance"
    distance_client = this->create_client<DistanceSrv>("distance");
  }

  // 3-2) 连接服务：等待服务可用
  bool connect_server() {
    // 等待周期：每次 wait_for_service 超时 1s
    while (!distance_client->wait_for_service(1s)) {
      if (!rclcpp::ok()) {
        RCLCPP_INFO(this->get_logger(), "客户端退出！");
        return false;
      }
      RCLCPP_INFO(this->get_logger(), "服务连接中，请稍候...");
    }
    return true;
  }

  // 3-3) 发送请求：把目标点坐标封装进 Distance 请求并 async_send_request
  rclcpp::Client<DistanceSrv>::FutureAndRequestId send_distance(float x, float y, float theta) {
    auto distance_request = std::make_shared<DistanceSrv::Request>();
    distance_request->x = x;
    distance_request->y = y;
    distance_request->theta = theta;  // 该字段在服务端当前版本未使用，但保留透传
    return distance_client->async_send_request(distance_request);
  }

private:
  // 客户端句柄：保持对服务的连接能力
  rclcpp::Client<DistanceSrv>::SharedPtr distance_client;
};

int main(int argc, char const *argv[]) {
  // 1) 初始化 ROS2
  rclcpp::init(argc, argv);

  // 2) 创建客户端节点
  auto client = std::make_shared<ExeDistanceClient>();

  // 3) 处理传入的参数：期望 3 个值：x y theta
  if (argc != 5) {
    RCLCPP_INFO(client->get_logger(), "请传入目标的位姿参数:(x,y,theta)");
    return 1;
  }

  // 4) 解析命令行参数
  float x = atof(argv[1]);
  float y = atof(argv[2]);
  float theta = atof(argv[3]);

  // 5) 服务连接
  bool flag = client->connect_server();
  if (!flag) {
    RCLCPP_INFO(client->get_logger(), "服务连接失败!");
    return 1;
  }

  // 6) 发送请求并等待响应
  auto distance_future = client->send_distance(x, y, theta);

  if (rclcpp::spin_until_future_complete(client, distance_future) ==
      rclcpp::FutureReturnCode::SUCCESS) {
    // 7) 打印结果：服务端填充的 distance
    RCLCPP_INFO(client->get_logger(), "两只乌龟相距%.2f米。", distance_future.get()->distance);
  } else {
    RCLCPP_INFO(client->get_logger(), "获取距离服务失败!");
  }

  // 8) 释放资源
  rclcpp::shutdown();
  return 0;
}
