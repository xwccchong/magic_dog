// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from roarm_msgs:srv/GetPoseCmd.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__GET_POSE_CMD__STRUCT_H_
#define ROARM_MSGS__SRV__DETAIL__GET_POSE_CMD__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/GetPoseCmd in the package roarm_msgs.
typedef struct roarm_msgs__srv__GetPoseCmd_Request
{
  uint8_t structure_needs_at_least_one_member;
} roarm_msgs__srv__GetPoseCmd_Request;

// Struct for a sequence of roarm_msgs__srv__GetPoseCmd_Request.
typedef struct roarm_msgs__srv__GetPoseCmd_Request__Sequence
{
  roarm_msgs__srv__GetPoseCmd_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} roarm_msgs__srv__GetPoseCmd_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/GetPoseCmd in the package roarm_msgs.
typedef struct roarm_msgs__srv__GetPoseCmd_Response
{
  double x;
  double y;
  double z;
  double roll;
  double pitch;
  double yaw;
} roarm_msgs__srv__GetPoseCmd_Response;

// Struct for a sequence of roarm_msgs__srv__GetPoseCmd_Response.
typedef struct roarm_msgs__srv__GetPoseCmd_Response__Sequence
{
  roarm_msgs__srv__GetPoseCmd_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} roarm_msgs__srv__GetPoseCmd_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROARM_MSGS__SRV__DETAIL__GET_POSE_CMD__STRUCT_H_
