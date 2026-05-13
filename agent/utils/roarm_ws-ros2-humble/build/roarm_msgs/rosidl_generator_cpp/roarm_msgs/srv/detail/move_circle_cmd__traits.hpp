// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from roarm_msgs:srv/MoveCircleCmd.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__TRAITS_HPP_
#define ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "roarm_msgs/srv/detail/move_circle_cmd__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace roarm_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MoveCircleCmd_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: x0
  {
    out << "x0: ";
    rosidl_generator_traits::value_to_yaml(msg.x0, out);
    out << ", ";
  }

  // member: y0
  {
    out << "y0: ";
    rosidl_generator_traits::value_to_yaml(msg.y0, out);
    out << ", ";
  }

  // member: z0
  {
    out << "z0: ";
    rosidl_generator_traits::value_to_yaml(msg.z0, out);
    out << ", ";
  }

  // member: x1
  {
    out << "x1: ";
    rosidl_generator_traits::value_to_yaml(msg.x1, out);
    out << ", ";
  }

  // member: y1
  {
    out << "y1: ";
    rosidl_generator_traits::value_to_yaml(msg.y1, out);
    out << ", ";
  }

  // member: z1
  {
    out << "z1: ";
    rosidl_generator_traits::value_to_yaml(msg.z1, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MoveCircleCmd_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x0
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x0: ";
    rosidl_generator_traits::value_to_yaml(msg.x0, out);
    out << "\n";
  }

  // member: y0
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y0: ";
    rosidl_generator_traits::value_to_yaml(msg.y0, out);
    out << "\n";
  }

  // member: z0
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z0: ";
    rosidl_generator_traits::value_to_yaml(msg.z0, out);
    out << "\n";
  }

  // member: x1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x1: ";
    rosidl_generator_traits::value_to_yaml(msg.x1, out);
    out << "\n";
  }

  // member: y1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y1: ";
    rosidl_generator_traits::value_to_yaml(msg.y1, out);
    out << "\n";
  }

  // member: z1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z1: ";
    rosidl_generator_traits::value_to_yaml(msg.z1, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MoveCircleCmd_Request & msg, bool use_flow_style = false)
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
  const roarm_msgs::srv::MoveCircleCmd_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  roarm_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use roarm_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const roarm_msgs::srv::MoveCircleCmd_Request & msg)
{
  return roarm_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<roarm_msgs::srv::MoveCircleCmd_Request>()
{
  return "roarm_msgs::srv::MoveCircleCmd_Request";
}

template<>
inline const char * name<roarm_msgs::srv::MoveCircleCmd_Request>()
{
  return "roarm_msgs/srv/MoveCircleCmd_Request";
}

template<>
struct has_fixed_size<roarm_msgs::srv::MoveCircleCmd_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<roarm_msgs::srv::MoveCircleCmd_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<roarm_msgs::srv::MoveCircleCmd_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace roarm_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MoveCircleCmd_Response & msg,
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
  const MoveCircleCmd_Response & msg,
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

inline std::string to_yaml(const MoveCircleCmd_Response & msg, bool use_flow_style = false)
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
  const roarm_msgs::srv::MoveCircleCmd_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  roarm_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use roarm_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const roarm_msgs::srv::MoveCircleCmd_Response & msg)
{
  return roarm_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<roarm_msgs::srv::MoveCircleCmd_Response>()
{
  return "roarm_msgs::srv::MoveCircleCmd_Response";
}

template<>
inline const char * name<roarm_msgs::srv::MoveCircleCmd_Response>()
{
  return "roarm_msgs/srv/MoveCircleCmd_Response";
}

template<>
struct has_fixed_size<roarm_msgs::srv::MoveCircleCmd_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<roarm_msgs::srv::MoveCircleCmd_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<roarm_msgs::srv::MoveCircleCmd_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<roarm_msgs::srv::MoveCircleCmd>()
{
  return "roarm_msgs::srv::MoveCircleCmd";
}

template<>
inline const char * name<roarm_msgs::srv::MoveCircleCmd>()
{
  return "roarm_msgs/srv/MoveCircleCmd";
}

template<>
struct has_fixed_size<roarm_msgs::srv::MoveCircleCmd>
  : std::integral_constant<
    bool,
    has_fixed_size<roarm_msgs::srv::MoveCircleCmd_Request>::value &&
    has_fixed_size<roarm_msgs::srv::MoveCircleCmd_Response>::value
  >
{
};

template<>
struct has_bounded_size<roarm_msgs::srv::MoveCircleCmd>
  : std::integral_constant<
    bool,
    has_bounded_size<roarm_msgs::srv::MoveCircleCmd_Request>::value &&
    has_bounded_size<roarm_msgs::srv::MoveCircleCmd_Response>::value
  >
{
};

template<>
struct is_service<roarm_msgs::srv::MoveCircleCmd>
  : std::true_type
{
};

template<>
struct is_service_request<roarm_msgs::srv::MoveCircleCmd_Request>
  : std::true_type
{
};

template<>
struct is_service_response<roarm_msgs::srv::MoveCircleCmd_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__TRAITS_HPP_
