#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__msg__ServoStatus() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__msg__ServoStatus__init(msg: *mut ServoStatus) -> bool;
    fn roarm_msgs__msg__ServoStatus__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServoStatus>, size: usize) -> bool;
    fn roarm_msgs__msg__ServoStatus__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServoStatus>);
    fn roarm_msgs__msg__ServoStatus__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServoStatus>, out_seq: *mut rosidl_runtime_rs::Sequence<ServoStatus>) -> bool;
}

// Corresponds to roarm_msgs__msg__ServoStatus
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Message

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServoStatus {
    /// will contains integer code
    pub code: i8,

    /// will contain explanatory message
    pub message: rosidl_runtime_rs::String,

}

impl ServoStatus {
    /// Status types (should reflect StatusCode from moveit_servo/utils/datatype.hpp)
    pub const INVALID: i8 = -1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const NO_WARNING: i8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const DECELERATE_FOR_APPROACHING_SINGULARITY: i8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const HALT_FOR_SINGULARITY: i8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const DECELERATE_FOR_LEAVING_SINGULARITY: i8 = 3;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const DECELERATE_FOR_COLLISION: i8 = 4;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const HALT_FOR_COLLISION: i8 = 5;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const JOINT_BOUND: i8 = 6;

}


impl Default for ServoStatus {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__msg__ServoStatus__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__msg__ServoStatus__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServoStatus {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__msg__ServoStatus__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__msg__ServoStatus__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__msg__ServoStatus__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServoStatus {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServoStatus where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/msg/ServoStatus";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__msg__ServoStatus() }
  }
}


