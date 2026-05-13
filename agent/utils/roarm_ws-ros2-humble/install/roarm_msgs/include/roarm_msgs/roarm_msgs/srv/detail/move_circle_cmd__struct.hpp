// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from roarm_msgs:srv/MoveCircleCmd.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__STRUCT_HPP_
#define ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Request __attribute__((deprecated))
#else
# define DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Request __declspec(deprecated)
#endif

namespace roarm_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct MoveCircleCmd_Request_
{
  using Type = MoveCircleCmd_Request_<ContainerAllocator>;

  explicit MoveCircleCmd_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x0 = 0.0;
      this->y0 = 0.0;
      this->z0 = 0.0;
      this->x1 = 0.0;
      this->y1 = 0.0;
      this->z1 = 0.0;
    }
  }

  explicit MoveCircleCmd_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x0 = 0.0;
      this->y0 = 0.0;
      this->z0 = 0.0;
      this->x1 = 0.0;
      this->y1 = 0.0;
      this->z1 = 0.0;
    }
  }

  // field types and members
  using _x0_type =
    double;
  _x0_type x0;
  using _y0_type =
    double;
  _y0_type y0;
  using _z0_type =
    double;
  _z0_type z0;
  using _x1_type =
    double;
  _x1_type x1;
  using _y1_type =
    double;
  _y1_type y1;
  using _z1_type =
    double;
  _z1_type z1;

  // setters for named parameter idiom
  Type & set__x0(
    const double & _arg)
  {
    this->x0 = _arg;
    return *this;
  }
  Type & set__y0(
    const double & _arg)
  {
    this->y0 = _arg;
    return *this;
  }
  Type & set__z0(
    const double & _arg)
  {
    this->z0 = _arg;
    return *this;
  }
  Type & set__x1(
    const double & _arg)
  {
    this->x1 = _arg;
    return *this;
  }
  Type & set__y1(
    const double & _arg)
  {
    this->y1 = _arg;
    return *this;
  }
  Type & set__z1(
    const double & _arg)
  {
    this->z1 = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Request
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Request
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MoveCircleCmd_Request_ & other) const
  {
    if (this->x0 != other.x0) {
      return false;
    }
    if (this->y0 != other.y0) {
      return false;
    }
    if (this->z0 != other.z0) {
      return false;
    }
    if (this->x1 != other.x1) {
      return false;
    }
    if (this->y1 != other.y1) {
      return false;
    }
    if (this->z1 != other.z1) {
      return false;
    }
    return true;
  }
  bool operator!=(const MoveCircleCmd_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MoveCircleCmd_Request_

// alias to use template instance with default allocator
using MoveCircleCmd_Request =
  roarm_msgs::srv::MoveCircleCmd_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace roarm_msgs


#ifndef _WIN32
# define DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Response __attribute__((deprecated))
#else
# define DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Response __declspec(deprecated)
#endif

namespace roarm_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct MoveCircleCmd_Response_
{
  using Type = MoveCircleCmd_Response_<ContainerAllocator>;

  explicit MoveCircleCmd_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit MoveCircleCmd_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Response
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__roarm_msgs__srv__MoveCircleCmd_Response
    std::shared_ptr<roarm_msgs::srv::MoveCircleCmd_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MoveCircleCmd_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const MoveCircleCmd_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MoveCircleCmd_Response_

// alias to use template instance with default allocator
using MoveCircleCmd_Response =
  roarm_msgs::srv::MoveCircleCmd_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace roarm_msgs

namespace roarm_msgs
{

namespace srv
{

struct MoveCircleCmd
{
  using Request = roarm_msgs::srv::MoveCircleCmd_Request;
  using Response = roarm_msgs::srv::MoveCircleCmd_Response;
};

}  // namespace srv

}  // namespace roarm_msgs

#endif  // ROARM_MSGS__SRV__DETAIL__MOVE_CIRCLE_CMD__STRUCT_HPP_
