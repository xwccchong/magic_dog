// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from roarm_msgs:srv/MoveJointCmd.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__STRUCT_HPP_
#define ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__roarm_msgs__srv__MoveJointCmd_Request __attribute__((deprecated))
#else
# define DEPRECATED__roarm_msgs__srv__MoveJointCmd_Request __declspec(deprecated)
#endif

namespace roarm_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct MoveJointCmd_Request_
{
  using Type = MoveJointCmd_Request_<ContainerAllocator>;

  explicit MoveJointCmd_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->roll = 0.0;
      this->pitch = 0.0;
      this->yaw = 0.0;
    }
  }

  explicit MoveJointCmd_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->roll = 0.0;
      this->pitch = 0.0;
      this->yaw = 0.0;
    }
  }

  // field types and members
  using _x_type =
    double;
  _x_type x;
  using _y_type =
    double;
  _y_type y;
  using _z_type =
    double;
  _z_type z;
  using _roll_type =
    double;
  _roll_type roll;
  using _pitch_type =
    double;
  _pitch_type pitch;
  using _yaw_type =
    double;
  _yaw_type yaw;

  // setters for named parameter idiom
  Type & set__x(
    const double & _arg)
  {
    this->x = _arg;
    return *this;
  }
  Type & set__y(
    const double & _arg)
  {
    this->y = _arg;
    return *this;
  }
  Type & set__z(
    const double & _arg)
  {
    this->z = _arg;
    return *this;
  }
  Type & set__roll(
    const double & _arg)
  {
    this->roll = _arg;
    return *this;
  }
  Type & set__pitch(
    const double & _arg)
  {
    this->pitch = _arg;
    return *this;
  }
  Type & set__yaw(
    const double & _arg)
  {
    this->yaw = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__roarm_msgs__srv__MoveJointCmd_Request
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__roarm_msgs__srv__MoveJointCmd_Request
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MoveJointCmd_Request_ & other) const
  {
    if (this->x != other.x) {
      return false;
    }
    if (this->y != other.y) {
      return false;
    }
    if (this->z != other.z) {
      return false;
    }
    if (this->roll != other.roll) {
      return false;
    }
    if (this->pitch != other.pitch) {
      return false;
    }
    if (this->yaw != other.yaw) {
      return false;
    }
    return true;
  }
  bool operator!=(const MoveJointCmd_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MoveJointCmd_Request_

// alias to use template instance with default allocator
using MoveJointCmd_Request =
  roarm_msgs::srv::MoveJointCmd_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace roarm_msgs


#ifndef _WIN32
# define DEPRECATED__roarm_msgs__srv__MoveJointCmd_Response __attribute__((deprecated))
#else
# define DEPRECATED__roarm_msgs__srv__MoveJointCmd_Response __declspec(deprecated)
#endif

namespace roarm_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct MoveJointCmd_Response_
{
  using Type = MoveJointCmd_Response_<ContainerAllocator>;

  explicit MoveJointCmd_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit MoveJointCmd_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__roarm_msgs__srv__MoveJointCmd_Response
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__roarm_msgs__srv__MoveJointCmd_Response
    std::shared_ptr<roarm_msgs::srv::MoveJointCmd_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MoveJointCmd_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const MoveJointCmd_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MoveJointCmd_Response_

// alias to use template instance with default allocator
using MoveJointCmd_Response =
  roarm_msgs::srv::MoveJointCmd_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace roarm_msgs

namespace roarm_msgs
{

namespace srv
{

struct MoveJointCmd
{
  using Request = roarm_msgs::srv::MoveJointCmd_Request;
  using Response = roarm_msgs::srv::MoveJointCmd_Response;
};

}  // namespace srv

}  // namespace roarm_msgs

#endif  // ROARM_MSGS__SRV__DETAIL__MOVE_JOINT_CMD__STRUCT_HPP_
