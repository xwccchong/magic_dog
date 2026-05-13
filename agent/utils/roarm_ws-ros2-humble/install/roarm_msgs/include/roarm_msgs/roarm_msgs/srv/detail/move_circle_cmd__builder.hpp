// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from roarm_msgs:srv/MoveCircleCmd.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__BUILDER_HPP_
#define ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "roarm_msgs/srv/detail/move_circle_cmd__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace roarm_msgs
{

namespace srv
{

namespace builder
{

class Init_MoveCircleCmd_Request_z1
{
public:
  explicit Init_MoveCircleCmd_Request_z1(::roarm_msgs::srv::MoveCircleCmd_Request & msg)
  : msg_(msg)
  {}
  ::roarm_msgs::srv::MoveCircleCmd_Request z1(::roarm_msgs::srv::MoveCircleCmd_Request::_z1_type arg)
  {
    msg_.z1 = std::move(arg);
    return std::move(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Request msg_;
};

class Init_MoveCircleCmd_Request_y1
{
public:
  explicit Init_MoveCircleCmd_Request_y1(::roarm_msgs::srv::MoveCircleCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveCircleCmd_Request_z1 y1(::roarm_msgs::srv::MoveCircleCmd_Request::_y1_type arg)
  {
    msg_.y1 = std::move(arg);
    return Init_MoveCircleCmd_Request_z1(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Request msg_;
};

class Init_MoveCircleCmd_Request_x1
{
public:
  explicit Init_MoveCircleCmd_Request_x1(::roarm_msgs::srv::MoveCircleCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveCircleCmd_Request_y1 x1(::roarm_msgs::srv::MoveCircleCmd_Request::_x1_type arg)
  {
    msg_.x1 = std::move(arg);
    return Init_MoveCircleCmd_Request_y1(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Request msg_;
};

class Init_MoveCircleCmd_Request_z0
{
public:
  explicit Init_MoveCircleCmd_Request_z0(::roarm_msgs::srv::MoveCircleCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveCircleCmd_Request_x1 z0(::roarm_msgs::srv::MoveCircleCmd_Request::_z0_type arg)
  {
    msg_.z0 = std::move(arg);
    return Init_MoveCircleCmd_Request_x1(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Request msg_;
};

class Init_MoveCircleCmd_Request_y0
{
public:
  explicit Init_MoveCircleCmd_Request_y0(::roarm_msgs::srv::MoveCircleCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveCircleCmd_Request_z0 y0(::roarm_msgs::srv::MoveCircleCmd_Request::_y0_type arg)
  {
    msg_.y0 = std::move(arg);
    return Init_MoveCircleCmd_Request_z0(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Request msg_;
};

class Init_MoveCircleCmd_Request_x0
{
public:
  Init_MoveCircleCmd_Request_x0()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MoveCircleCmd_Request_y0 x0(::roarm_msgs::srv::MoveCircleCmd_Request::_x0_type arg)
  {
    msg_.x0 = std::move(arg);
    return Init_MoveCircleCmd_Request_y0(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::roarm_msgs::srv::MoveCircleCmd_Request>()
{
  return roarm_msgs::srv::builder::Init_MoveCircleCmd_Request_x0();
}

}  // namespace roarm_msgs


namespace roarm_msgs
{

namespace srv
{

namespace builder
{

class Init_MoveCircleCmd_Response_message
{
public:
  explicit Init_MoveCircleCmd_Response_message(::roarm_msgs::srv::MoveCircleCmd_Response & msg)
  : msg_(msg)
  {}
  ::roarm_msgs::srv::MoveCircleCmd_Response message(::roarm_msgs::srv::MoveCircleCmd_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Response msg_;
};

class Init_MoveCircleCmd_Response_success
{
public:
  Init_MoveCircleCmd_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MoveCircleCmd_Response_message success(::roarm_msgs::srv::MoveCircleCmd_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_MoveCircleCmd_Response_message(msg_);
  }

private:
  ::roarm_msgs::srv::MoveCircleCmd_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::roarm_msgs::srv::MoveCircleCmd_Response>()
{
  return roarm_msgs::srv::builder::Init_MoveCircleCmd_Response_success();
}

}  // namespace roarm_msgs

#endif  // ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__BUILDER_HPP_
