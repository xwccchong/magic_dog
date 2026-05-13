// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from roarm_msgs:srv/ServoCommandType.idl
// generated code does not contain a copyright notice

#ifndef ROARM_MSGS__SRV__DETAIL__SERVO_COMMAND_TYPE__STRUCT_H_
#define ROARM_MSGS__SRV__DETAIL__SERVO_COMMAND_TYPE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'JOINT_JOG'.
enum
{
  roarm_msgs__srv__ServoCommandType_Request__JOINT_JOG = 0
};

/// Constant 'TWIST'.
enum
{
  roarm_msgs__srv__ServoCommandType_Request__TWIST = 1
};

/// Constant 'POSE'.
enum
{
  roarm_msgs__srv__ServoCommandType_Request__POSE = 2
};

/// Struct defined in srv/ServoCommandType in the package roarm_msgs.
typedef struct roarm_msgs__srv__ServoCommandType_Request
{
  /// Request Field
  int8_t command_type;
} roarm_msgs__srv__ServoCommandType_Request;

// Struct for a sequence of roarm_msgs__srv__ServoCommandType_Request.
typedef struct roarm_msgs__srv__ServoCommandType_Request__Sequence
{
  roarm_msgs__srv__ServoCommandType_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} roarm_msgs__srv__ServoCommandType_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/ServoCommandType in the package roarm_msgs.
typedef struct roarm_msgs__srv__ServoCommandType_Response
{
  bool success;
} roarm_msgs__srv__ServoCommandType_Response;

// Struct for a sequence of roarm_msgs__srv__ServoCommandType_Response.
typedef struct roarm_msgs__srv__ServoCommandType_Response__Sequence
{
  roarm_msgs__srv__ServoCommandType_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} roarm_msgs__srv__ServoCommandType_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROARM_MSGS__SRV__DETAIL__SERVO_COMMAND_TYPE__STRUCT_H_
