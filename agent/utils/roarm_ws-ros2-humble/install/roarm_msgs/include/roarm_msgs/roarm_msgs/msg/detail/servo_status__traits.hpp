// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from roarm_msgs:msg/ServoStatus.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__MSG__DETAIL__SERVO_STATUS__TRAITS_HPP_
#define ROARM_MSGS__MSG__DETAIL__SERVO_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "roarm_msgs/msg/detail/servo_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace roarm_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const ServoStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: code
  {
    out << "code: ";
    rosidl_generator_traits::value_to_yaml(msg.code, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ServoStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: code
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "code: ";
    rosidl_generator_traits::value_to_yaml(msg.code, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ServoStatus & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace roarm_msgs

namespace rosidl_generator_traits
{

[[deprecated("use roarm_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const roarm_msgs::msg::ServoStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  roarm_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use roarm_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const roarm_msgs::msg::ServoStatus & msg)
{
  return roarm_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<roarm_msgs::msg::ServoStatus>()
{
  return "roarm_msgs::msg::ServoStatus";
}

template<>
inline const char * name<roarm_msgs::msg::ServoStatus>()
{
  return "roarm_msgs/msg/ServoStatus";
}

template<>
struct has_fixed_size<roarm_msgs::msg::ServoStatus>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<roarm_msgs::msg::ServoStatus>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<roarm_msgs::msg::ServoStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROARM_MSGS__MSG__DETAIL__SERVO_STATUS__TRAITS_HPP_
