// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from roarm_msgs:srv/MoveJointCmd.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__BUILDER_HPP_
#define ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "roarm_msgs/srv/detail/move_joint_cmd__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace roarm_msgs
{

namespace srv
{

namespace builder
{

class Init_MoveJointCmd_Request_yaw
{
public:
  explicit Init_MoveJointCmd_Request_yaw(::roarm_msgs::srv::MoveJointCmd_Request & msg)
  : msg_(msg)
  {}
  ::roarm_msgs::srv::MoveJointCmd_Request yaw(::roarm_msgs::srv::MoveJointCmd_Request::_yaw_type arg)
  {
    msg_.yaw = std::move(arg);
    return std::move(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Request msg_;
};

class Init_MoveJointCmd_Request_pitch
{
public:
  explicit Init_MoveJointCmd_Request_pitch(::roarm_msgs::srv::MoveJointCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveJointCmd_Request_yaw pitch(::roarm_msgs::srv::MoveJointCmd_Request::_pitch_type arg)
  {
    msg_.pitch = std::move(arg);
    return Init_MoveJointCmd_Request_yaw(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Request msg_;
};

class Init_MoveJointCmd_Request_roll
{
public:
  explicit Init_MoveJointCmd_Request_roll(::roarm_msgs::srv::MoveJointCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveJointCmd_Request_pitch roll(::roarm_msgs::srv::MoveJointCmd_Request::_roll_type arg)
  {
    msg_.roll = std::move(arg);
    return Init_MoveJointCmd_Request_pitch(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Request msg_;
};

class Init_MoveJointCmd_Request_z
{
public:
  explicit Init_MoveJointCmd_Request_z(::roarm_msgs::srv::MoveJointCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveJointCmd_Request_roll z(::roarm_msgs::srv::MoveJointCmd_Request::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_MoveJointCmd_Request_roll(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Request msg_;
};

class Init_MoveJointCmd_Request_y
{
public:
  explicit Init_MoveJointCmd_Request_y(::roarm_msgs::srv::MoveJointCmd_Request & msg)
  : msg_(msg)
  {}
  Init_MoveJointCmd_Request_z y(::roarm_msgs::srv::MoveJointCmd_Request::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_MoveJointCmd_Request_z(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Request msg_;
};

class Init_MoveJointCmd_Request_x
{
public:
  Init_MoveJointCmd_Request_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MoveJointCmd_Request_y x(::roarm_msgs::srv::MoveJointCmd_Request::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_MoveJointCmd_Request_y(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::roarm_msgs::srv::MoveJointCmd_Request>()
{
  return roarm_msgs::srv::builder::Init_MoveJointCmd_Request_x();
}

}  // namespace roarm_msgs


namespace roarm_msgs
{

namespace srv
{

namespace builder
{

class Init_MoveJointCmd_Response_message
{
public:
  explicit Init_MoveJointCmd_Response_message(::roarm_msgs::srv::MoveJointCmd_Response & msg)
  : msg_(msg)
  {}
  ::roarm_msgs::srv::MoveJointCmd_Response message(::roarm_msgs::srv::MoveJointCmd_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Response msg_;
};

class Init_MoveJointCmd_Response_success
{
public:
  Init_MoveJointCmd_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MoveJointCmd_Response_message success(::roarm_msgs::srv::MoveJointCmd_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_MoveJointCmd_Response_message(msg_);
  }

private:
  ::roarm_msgs::srv::MoveJointCmd_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::roarm_msgs::srv::MoveJointCmd_Response>()
{
  return roarm_msgs::srv::builder::Init_MoveJointCmd_Response_success();
}

}  // namespace roarm_msgs

#endif  // ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__BUILDER_HPP_
