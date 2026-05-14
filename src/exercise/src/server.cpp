#include "rclcpp/rclcpp.hpp"
#include "base_interface/srv/distance.hpp"
#include "turtlesim/msg/pose.hpp"
#include "turtlesim/srv/spawn.hpp"

using namespace std::chrono_literals;

// 计算两点距离服务端：订阅 turtle1 位姿，并在收到客户端的目标坐标请求后返回欧氏距离。
// 通常运行流程：server.launch.py 启动 turtlesim_node + 本服务节点；client.launch.py 调用服务 /distance。
// 说明：turtle 坐标来自订阅的 /turtle1/pose，目标坐标来自 Distance 服务请求中的 x/y。

using DistanceSrv = base_interface::srv::Distance;

// 1) 节点类：继承 rclcpp::Node
class ExeDistanceServer : public rclcpp::Node {
public:
  // 2) 构造函数：初始化节点并建立通信
  ExeDistanceServer()
  : Node("exe_distance_server"),
    turtle1_x(0.0f),
    turtle1_y(0.0f) {
    // 3-1) 创建乌龟姿态订阅方：订阅 /turtle1/pose，回调中更新 turtle1 当前坐标
    pose_sub = this->create_subscription<turtlesim::msg::Pose>(
      "/turtle1/pose",
      10,
      std::bind(&ExeDistanceServer::poseCallBack, this, std::placeholders::_1));

    // 3-2) 创建服务端：提供名为 "distance" 的 Distance 服务
    // 回调签名：request/response 分别对应请求与响应
    distance_server = this->create_service<DistanceSrv>(
      "distance",
      std::bind(&ExeDistanceServer::distanceCallBack, this, std::placeholders::_1, std::placeholders::_2));
  }

private:
  // 3-1-1) 订阅回调：从 turtlesim 的 Pose 消息中提取 x/y
  void poseCallBack(const turtlesim::msg::Pose::SharedPtr pose) {
    turtle1_x = static_cast<float>(pose->x);
    turtle1_y = static_cast<float>(pose->y);
  }

  // 3-2-1) 服务回调：解析目标坐标，计算目标点与 turtle1 当前坐标的距离并返回
  void distanceCallBack(
    const DistanceSrv::Request::SharedPtr request,
    DistanceSrv::Response::SharedPtr response) {
    // 解析目标值（客户端传入的目标坐标）
    float goal_x = request->x;
    float goal_y = request->y;

    // 距离计算：欧氏距离 d = sqrt((dx)^2 + (dy)^2)
    float dx = goal_x - turtle1_x;
    float dy = goal_y - turtle1_y;

    response->distance = std::sqrt(dx * dx + dy * dy);

    // 输出日志：便于调试核对
    RCLCPP_INFO(
      this->get_logger(),
      "目标坐标:(%.2f, %.2f), 当前turtle1:(%.2f, %.2f), 距离:%.2f",
      goal_x, goal_y, turtle1_x, turtle1_y, response->distance);
  }

  // 订阅句柄：保持订阅关系
  rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_sub;

  // 服务句柄：保持服务可用
  rclcpp::Service<DistanceSrv>::SharedPtr distance_server;

  // 缓存 turtle1 当前坐标（由 pose 订阅回调更新）
  float turtle1_x;
  float turtle1_y;
};

int main(int argc, char const *argv[]) {
  // 1) 初始化 ROS2
  rclcpp::init(argc, argv);

  // 2) 创建服务节点实例
  auto node = std::make_shared<ExeDistanceServer>();

  // 3) 进入 spin：持续处理订阅与服务回调
  rclcpp::spin(node);

  // 4) 释放资源
  rclcpp::shutdown();
  return 0;
}
