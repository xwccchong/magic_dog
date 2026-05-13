// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from roarm_msgs:srv/MoveCircleCmd.idl
// generated code does not contain a copyright notice
#include "roarm_msgs/srv/detail/move_circle_cmd__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
roarm_msgs__srv__MoveCircleCmd_Request__init(roarm_msgs__srv__MoveCircleCmd_Request * msg)
{
  if (!msg) {
    return false;
  }
  // x0
  // y0
  // z0
  // x1
  // y1
  // z1
  return true;
}

void
roarm_msgs__srv__MoveCircleCmd_Request__fini(roarm_msgs__srv__MoveCircleCmd_Request * msg)
{
  if (!msg) {
    return;
  }
  // x0
  // y0
  // z0
  // x1
  // y1
  // z1
}

bool
roarm_msgs__srv__MoveCircleCmd_Request__are_equal(const roarm_msgs__srv__MoveCircleCmd_Request * lhs, const roarm_msgs__srv__MoveCircleCmd_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // x0
  if (lhs->x0 != rhs->x0) {
    return false;
  }
  // y0
  if (lhs->y0 != rhs->y0) {
    return false;
  }
  // z0
  if (lhs->z0 != rhs->z0) {
    return false;
  }
  // x1
  if (lhs->x1 != rhs->x1) {
    return false;
  }
  // y1
  if (lhs->y1 != rhs->y1) {
    return false;
  }
  // z1
  if (lhs->z1 != rhs->z1) {
    return false;
  }
  return true;
}

bool
roarm_msgs__srv__MoveCircleCmd_Request__copy(
  const roarm_msgs__srv__MoveCircleCmd_Request * input,
  roarm_msgs__srv__MoveCircleCmd_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // x0
  output->x0 = input->x0;
  // y0
  output->y0 = input->y0;
  // z0
  output->z0 = input->z0;
  // x1
  output->x1 = input->x1;
  // y1
  output->y1 = input->y1;
  // z1
  output->z1 = input->z1;
  return true;
}

roarm_msgs__srv__MoveCircleCmd_Request *
roarm_msgs__srv__MoveCircleCmd_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  roarm_msgs__srv__MoveCircleCmd_Request * msg = (roarm_msgs__srv__MoveCircleCmd_Request *)allocator.allocate(sizeof(roarm_msgs__srv__MoveCircleCmd_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(roarm_msgs__srv__MoveCircleCmd_Request));
  bool success = roarm_msgs__srv__MoveCircleCmd_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
roarm_msgs__srv__MoveCircleCmd_Request__destroy(roarm_msgs__srv__MoveCircleCmd_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    roarm_msgs__srv__MoveCircleCmd_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
roarm_msgs__srv__MoveCircleCmd_Request__Sequence__init(roarm_msgs__srv__MoveCircleCmd_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  roarm_msgs__srv__MoveCircleCmd_Request * data = NULL;

  if (size) {
    data = (roarm_msgs__srv__MoveCircleCmd_Request *)allocator.zero_allocate(size, sizeof(roarm_msgs__srv__MoveCircleCmd_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = roarm_msgs__srv__MoveCircleCmd_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        roarm_msgs__srv__MoveCircleCmd_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
roarm_msgs__srv__MoveCircleCmd_Request__Sequence__fini(roarm_msgs__srv__MoveCircleCmd_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      roarm_msgs__srv__MoveCircleCmd_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

roarm_msgs__srv__MoveCircleCmd_Request__Sequence *
roarm_msgs__srv__MoveCircleCmd_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  roarm_msgs__srv__MoveCircleCmd_Request__Sequence * array = (roarm_msgs__srv__MoveCircleCmd_Request__Sequence *)allocator.allocate(sizeof(roarm_msgs__srv__MoveCircleCmd_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = roarm_msgs__srv__MoveCircleCmd_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
roarm_msgs__srv__MoveCircleCmd_Request__Sequence__destroy(roarm_msgs__srv__MoveCircleCmd_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    roarm_msgs__srv__MoveCircleCmd_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
roarm_msgs__srv__MoveCircleCmd_Request__Sequence__are_equal(const roarm_msgs__srv__MoveCircleCmd_Request__Sequence * lhs, const roarm_msgs__srv__MoveCircleCmd_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!roarm_msgs__srv__MoveCircleCmd_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
roarm_msgs__srv__MoveCircleCmd_Request__Sequence__copy(
  const roarm_msgs__srv__MoveCircleCmd_Request__Sequence * input,
  roarm_msgs__srv__MoveCircleCmd_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(roarm_msgs__srv__MoveCircleCmd_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    roarm_msgs__srv__MoveCircleCmd_Request * data =
      (roarm_msgs__srv__MoveCircleCmd_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!roarm_msgs__srv__MoveCircleCmd_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          roarm_msgs__srv__MoveCircleCmd_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!roarm_msgs__srv__MoveCircleCmd_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
roarm_msgs__srv__MoveCircleCmd_Response__init(roarm_msgs__srv__MoveCircleCmd_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    roarm_msgs__srv__MoveCircleCmd_Response__fini(msg);
    return false;
  }
  return true;
}

void
roarm_msgs__srv__MoveCircleCmd_Response__fini(roarm_msgs__srv__MoveCircleCmd_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
roarm_msgs__srv__MoveCircleCmd_Response__are_equal(const roarm_msgs__srv__MoveCircleCmd_Response * lhs, const roarm_msgs__srv__MoveCircleCmd_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
roarm_msgs__srv__MoveCircleCmd_Response__copy(
  const roarm_msgs__srv__MoveCircleCmd_Response * input,
  roarm_msgs__srv__MoveCircleCmd_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

roarm_msgs__srv__MoveCircleCmd_Response *
roarm_msgs__srv__MoveCircleCmd_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  roarm_msgs__srv__MoveCircleCmd_Response * msg = (roarm_msgs__srv__MoveCircleCmd_Response *)allocator.allocate(sizeof(roarm_msgs__srv__MoveCircleCmd_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(roarm_msgs__srv__MoveCircleCmd_Response));
  bool success = roarm_msgs__srv__MoveCircleCmd_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
roarm_msgs__srv__MoveCircleCmd_Response__destroy(roarm_msgs__srv__MoveCircleCmd_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    roarm_msgs__srv__MoveCircleCmd_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
roarm_msgs__srv__MoveCircleCmd_Response__Sequence__init(roarm_msgs__srv__MoveCircleCmd_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  roarm_msgs__srv__MoveCircleCmd_Response * data = NULL;

  if (size) {
    data = (roarm_msgs__srv__MoveCircleCmd_Response *)allocator.zero_allocate(size, sizeof(roarm_msgs__srv__MoveCircleCmd_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = roarm_msgs__srv__MoveCircleCmd_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        roarm_msgs__srv__MoveCircleCmd_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
roarm_msgs__srv__MoveCircleCmd_Response__Sequence__fini(roarm_msgs__srv__MoveCircleCmd_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      roarm_msgs__srv__MoveCircleCmd_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

roarm_msgs__srv__MoveCircleCmd_Response__Sequence *
roarm_msgs__srv__MoveCircleCmd_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  roarm_msgs__srv__MoveCircleCmd_Response__Sequence * array = (roarm_msgs__srv__MoveCircleCmd_Response__Sequence *)allocator.allocate(sizeof(roarm_msgs__srv__MoveCircleCmd_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = roarm_msgs__srv__MoveCircleCmd_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
roarm_msgs__srv__MoveCircleCmd_Response__Sequence__destroy(roarm_msgs__srv__MoveCircleCmd_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    roarm_msgs__srv__MoveCircleCmd_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
roarm_msgs__srv__MoveCircleCmd_Response__Sequence__are_equal(const roarm_msgs__srv__MoveCircleCmd_Response__Sequence * lhs, const roarm_msgs__srv__MoveCircleCmd_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!roarm_msgs__srv__MoveCircleCmd_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
roarm_msgs__srv__MoveCircleCmd_Response__Sequence__copy(
  const roarm_msgs__srv__MoveCircleCmd_Response__Sequence * input,
  roarm_msgs__srv__MoveCircleCmd_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(roarm_msgs__srv__MoveCircleCmd_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    roarm_msgs__srv__MoveCircleCmd_Response * data =
      (roarm_msgs__srv__MoveCircleCmd_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!roarm_msgs__srv__MoveCircleCmd_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          roarm_msgs__srv__MoveCircleCmd_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!roarm_msgs__srv__MoveCircleCmd_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
