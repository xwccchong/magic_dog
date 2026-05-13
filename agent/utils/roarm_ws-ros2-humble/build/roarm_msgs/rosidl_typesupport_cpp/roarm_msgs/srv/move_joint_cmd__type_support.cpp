// generated from rosidl_typesupport_cpp/resource/idl__type_support.cpp.em
// with input from roarm_msgs:srv/MoveJointCmd.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "roarm_msgs/srv/detail/move_joint_cmd__struct.hpp"
#include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
#include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace roarm_msgs
{

namespace srv
{

namespace rosidl_typesupport_cpp
{

typedef struct _MoveJointCmd_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _MoveJointCmd_Request_type_support_ids_t;

static const _MoveJointCmd_Request_type_support_ids_t _MoveJointCmd_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _MoveJointCmd_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _MoveJointCmd_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _MoveJointCmd_Request_type_support_symbol_names_t _MoveJointCmd_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, roarm_msgs, srv, MoveJointCmd_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, roarm_msgs, srv, MoveJointCmd_Request)),
  }
};

typedef struct _MoveJointCmd_Request_type_support_data_t
{
  void * data[2];
} _MoveJointCmd_Request_type_support_data_t;

static _MoveJointCmd_Request_type_support_data_t _MoveJointCmd_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _MoveJointCmd_Request_message_typesupport_map = {
  2,
  "roarm_msgs",
  &_MoveJointCmd_Request_message_typesupport_ids.typesupport_identifier[0],
  &_MoveJointCmd_Request_message_typesupport_symbol_names.symbol_name[0],
  &_MoveJointCmd_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t MoveJointCmd_Request_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_MoveJointCmd_Request_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace srv

}  // namespace roarm_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<roarm_msgs::srv::MoveJointCmd_Request>()
{
  return &::roarm_msgs::srv::rosidl_typesupport_cpp::MoveJointCmd_Request_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, roarm_msgs, srv, MoveJointCmd_Request)() {
  return get_message_type_support_handle<roarm_msgs::srv::MoveJointCmd_Request>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "roarm_msgs/srv/detail/move_joint_cmd__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace roarm_msgs
{

namespace srv
{

namespace rosidl_typesupport_cpp
{

typedef struct _MoveJointCmd_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _MoveJointCmd_Response_type_support_ids_t;

static const _MoveJointCmd_Response_type_support_ids_t _MoveJointCmd_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _MoveJointCmd_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _MoveJointCmd_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _MoveJointCmd_Response_type_support_symbol_names_t _MoveJointCmd_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, roarm_msgs, srv, MoveJointCmd_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, roarm_msgs, srv, MoveJointCmd_Response)),
  }
};

typedef struct _MoveJointCmd_Response_type_support_data_t
{
  void * data[2];
} _MoveJointCmd_Response_type_support_data_t;

static _MoveJointCmd_Response_type_support_data_t _MoveJointCmd_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _MoveJointCmd_Response_message_typesupport_map = {
  2,
  "roarm_msgs",
  &_MoveJointCmd_Response_message_typesupport_ids.typesupport_identifier[0],
  &_MoveJointCmd_Response_message_typesupport_symbol_names.symbol_name[0],
  &_MoveJointCmd_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t MoveJointCmd_Response_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_MoveJointCmd_Response_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace srv

}  // namespace roarm_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<roarm_msgs::srv::MoveJointCmd_Response>()
{
  return &::roarm_msgs::srv::rosidl_typesupport_cpp::MoveJointCmd_Response_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, roarm_msgs, srv, MoveJointCmd_Response)() {
  return get_message_type_support_handle<roarm_msgs::srv::MoveJointCmd_Response>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "roarm_msgs/srv/detail/move_joint_cmd__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/service_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace roarm_msgs
{

namespace srv
{

namespace rosidl_typesupport_cpp
{

typedef struct _MoveJointCmd_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _MoveJointCmd_type_support_ids_t;

static const _MoveJointCmd_type_support_ids_t _MoveJointCmd_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _MoveJointCmd_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _MoveJointCmd_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _MoveJointCmd_type_support_symbol_names_t _MoveJointCmd_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, roarm_msgs, srv, MoveJointCmd)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, roarm_msgs, srv, MoveJointCmd)),
  }
};

typedef struct _MoveJointCmd_type_support_data_t
{
  void * data[2];
} _MoveJointCmd_type_support_data_t;

static _MoveJointCmd_type_support_data_t _MoveJointCmd_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _MoveJointCmd_service_typesupport_map = {
  2,
  "roarm_msgs",
  &_MoveJointCmd_service_typesupport_ids.typesupport_identifier[0],
  &_MoveJointCmd_service_typesupport_symbol_names.symbol_name[0],
  &_MoveJointCmd_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t MoveJointCmd_service_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_MoveJointCmd_service_typesupport_map),
  ::rosidl_typesupport_cpp::get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace srv

}  // namespace roarm_msgs

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<roarm_msgs::srv::MoveJointCmd>()
{
  return &::roarm_msgs::srv::rosidl_typesupport_cpp::MoveJointCmd_service_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_cpp, roarm_msgs, srv, MoveJointCmd)() {
  return ::rosidl_typesupport_cpp::get_service_type_support_handle<roarm_msgs::srv::MoveJointCmd>();
}

#ifdef __cplusplus
}
#endif
