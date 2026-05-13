// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from roarm_msgs:msg/ServoStatus.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__MSG__DETAIL__SERVO_STATUS__BUILDER_HPP_
#define ROARM_MSGS__MSG__DETAIL__SERVO_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "roarm_msgs/msg/detail/servo_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace roarm_msgs
{

namespace msg
{

namespace builder
{

class Init_ServoStatus_message
{
public:
  explicit Init_ServoStatus_message(::roarm_msgs::msg::ServoStatus & msg)
  : msg_(msg)
  {}
  ::roarm_msgs::msg::ServoStatus message(::roarm_msgs::msg::ServoStatus::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::roarm_msgs::msg::ServoStatus msg_;
};

class Init_ServoStatus_code
{
public:
  Init_ServoStatus_code()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ServoStatus_message code(::roarm_msgs::msg::ServoStatus::_code_type arg)
  {
    msg_.code = std::move(arg);
    return Init_ServoStatus_message(msg_);
  }

private:
  ::roarm_msgs::msg::ServoStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::roarm_msgs::msg::ServoStatus>()
{
  return roarm_msgs::msg::builder::Init_ServoStatus_code();
}

}  // namespace roarm_msgs

#endif  // ROARM_MSGS__MSG__DETAIL__SERVO_STATUS__BUILDER_HPP_
