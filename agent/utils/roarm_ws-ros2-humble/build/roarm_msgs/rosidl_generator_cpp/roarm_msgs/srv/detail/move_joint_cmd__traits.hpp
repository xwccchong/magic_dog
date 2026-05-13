// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from roarm_msgs:srv/MoveJointCmd.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__TRAITS_HPP_
#define ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "roarm_msgs/srv/detail/move_joint_cmd__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace roarm_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MoveJointCmd_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: roll
  {
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << ", ";
  }

  // member: pitch
  {
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << ", ";
  }

  // member: yaw
  {
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MoveJointCmd_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: roll
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "roll: ";
    rosidl_generator_traits::value_to_yaml(msg.roll, out);
    out << "\n";
  }

  // member: pitch
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pitch: ";
    rosidl_generator_traits::value_to_yaml(msg.pitch, out);
    out << "\n";
  }

  // member: yaw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "yaw: ";
    rosidl_generator_traits::value_to_yaml(msg.yaw, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MoveJointCmd_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace roarm_msgs

namespace rosidl_generator_traits
{

[[deprecated("use roarm_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const roarm_msgs::srv::MoveJointCmd_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  roarm_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use roarm_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const roarm_msgs::srv::MoveJointCmd_Request & msg)
{
  return roarm_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<roarm_msgs::srv::MoveJointCmd_Request>()
{
  return "roarm_msgs::srv::MoveJointCmd_Request";
}

template<>
inline const char * name<roarm_msgs::srv::MoveJointCmd_Request>()
{
  return "roarm_msgs/srv/MoveJointCmd_Request";
}

template<>
struct has_fixed_size<roarm_msgs::srv::MoveJointCmd_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<roarm_msgs::srv::MoveJointCmd_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<roarm_msgs::srv::MoveJointCmd_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace roarm_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MoveJointCmd_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
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
  const MoveJointCmd_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
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

inline std::string to_yaml(const MoveJointCmd_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace roarm_msgs

namespace rosidl_generator_traits
{

[[deprecated("use roarm_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const roarm_msgs::srv::MoveJointCmd_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  roarm_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use roarm_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const roarm_msgs::srv::MoveJointCmd_Response & msg)
{
  return roarm_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<roarm_msgs::srv::MoveJointCmd_Response>()
{
  return "roarm_msgs::srv::MoveJointCmd_Response";
}

template<>
inline const char * name<roarm_msgs::srv::MoveJointCmd_Response>()
{
  return "roarm_msgs/srv/MoveJointCmd_Response";
}

template<>
struct has_fixed_size<roarm_msgs::srv::MoveJointCmd_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<roarm_msgs::srv::MoveJointCmd_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<roarm_msgs::srv::MoveJointCmd_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<roarm_msgs::srv::MoveJointCmd>()
{
  return "roarm_msgs::srv::MoveJointCmd";
}

template<>
inline const char * name<roarm_msgs::srv::MoveJointCmd>()
{
  return "roarm_msgs/srv/MoveJointCmd";
}

template<>
struct has_fixed_size<roarm_msgs::srv::MoveJointCmd>
  : std::integral_constant<
    bool,
    has_fixed_size<roarm_msgs::srv::MoveJointCmd_Request>::value &&
    has_fixed_size<roarm_msgs::srv::MoveJointCmd_Response>::value
  >
{
};

template<>
struct has_bounded_size<roarm_msgs::srv::MoveJointCmd>
  : std::integral_constant<
    bool,
    has_bounded_size<roarm_msgs::srv::MoveJointCmd_Request>::value &&
    has_bounded_size<roarm_msgs::srv::MoveJointCmd_Response>::value
  >
{
};

template<>
struct is_service<roarm_msgs::srv::MoveJointCmd>
  : std::true_type
{
};

template<>
struct is_service_request<roarm_msgs::srv::MoveJointCmd_Request>
  : std::true_type
{
};

template<>
struct is_service_response<roarm_msgs::srv::MoveJointCmd_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__TRAITS_HPP_
