#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__GetPoseCmd_Request() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__GetPoseCmd_Request__init(msg: *mut GetPoseCmd_Request) -> bool;
    fn roarm_msgs__srv__GetPoseCmd_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetPoseCmd_Request>, size: usize) -> bool;
    fn roarm_msgs__srv__GetPoseCmd_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetPoseCmd_Request>);
    fn roarm_msgs__srv__GetPoseCmd_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetPoseCmd_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetPoseCmd_Request>) -> bool;
}

// Corresponds to roarm_msgs__srv__GetPoseCmd_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetPoseCmd_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetPoseCmd_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__GetPoseCmd_Request__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__GetPoseCmd_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetPoseCmd_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__GetPoseCmd_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__GetPoseCmd_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__GetPoseCmd_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetPoseCmd_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetPoseCmd_Request where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/GetPoseCmd_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__GetPoseCmd_Request() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__GetPoseCmd_Response() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__GetPoseCmd_Response__init(msg: *mut GetPoseCmd_Response) -> bool;
    fn roarm_msgs__srv__GetPoseCmd_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetPoseCmd_Response>, size: usize) -> bool;
    fn roarm_msgs__srv__GetPoseCmd_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetPoseCmd_Response>);
    fn roarm_msgs__srv__GetPoseCmd_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetPoseCmd_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetPoseCmd_Response>) -> bool;
}

// Corresponds to roarm_msgs__srv__GetPoseCmd_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetPoseCmd_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub roll: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pitch: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub yaw: f64,

}



impl Default for GetPoseCmd_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__GetPoseCmd_Response__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__GetPoseCmd_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetPoseCmd_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__GetPoseCmd_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__GetPoseCmd_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__GetPoseCmd_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetPoseCmd_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetPoseCmd_Response where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/GetPoseCmd_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__GetPoseCmd_Response() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveJointCmd_Request() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__MoveJointCmd_Request__init(msg: *mut MoveJointCmd_Request) -> bool;
    fn roarm_msgs__srv__MoveJointCmd_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveJointCmd_Request>, size: usize) -> bool;
    fn roarm_msgs__srv__MoveJointCmd_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveJointCmd_Request>);
    fn roarm_msgs__srv__MoveJointCmd_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveJointCmd_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveJointCmd_Request>) -> bool;
}

// Corresponds to roarm_msgs__srv__MoveJointCmd_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveJointCmd_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub roll: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pitch: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub yaw: f64,

}



impl Default for MoveJointCmd_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__MoveJointCmd_Request__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__MoveJointCmd_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveJointCmd_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveJointCmd_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveJointCmd_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveJointCmd_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveJointCmd_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveJointCmd_Request where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/MoveJointCmd_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveJointCmd_Request() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveJointCmd_Response() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__MoveJointCmd_Response__init(msg: *mut MoveJointCmd_Response) -> bool;
    fn roarm_msgs__srv__MoveJointCmd_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveJointCmd_Response>, size: usize) -> bool;
    fn roarm_msgs__srv__MoveJointCmd_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveJointCmd_Response>);
    fn roarm_msgs__srv__MoveJointCmd_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveJointCmd_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveJointCmd_Response>) -> bool;
}

// Corresponds to roarm_msgs__srv__MoveJointCmd_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveJointCmd_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

}



impl Default for MoveJointCmd_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__MoveJointCmd_Response__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__MoveJointCmd_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveJointCmd_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveJointCmd_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveJointCmd_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveJointCmd_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveJointCmd_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveJointCmd_Response where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/MoveJointCmd_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveJointCmd_Response() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveCircleCmd_Request() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__MoveCircleCmd_Request__init(msg: *mut MoveCircleCmd_Request) -> bool;
    fn roarm_msgs__srv__MoveCircleCmd_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveCircleCmd_Request>, size: usize) -> bool;
    fn roarm_msgs__srv__MoveCircleCmd_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveCircleCmd_Request>);
    fn roarm_msgs__srv__MoveCircleCmd_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveCircleCmd_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveCircleCmd_Request>) -> bool;
}

// Corresponds to roarm_msgs__srv__MoveCircleCmd_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveCircleCmd_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub x0: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y0: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z0: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub x1: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y1: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z1: f64,

}



impl Default for MoveCircleCmd_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__MoveCircleCmd_Request__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__MoveCircleCmd_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveCircleCmd_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveCircleCmd_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveCircleCmd_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveCircleCmd_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveCircleCmd_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveCircleCmd_Request where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/MoveCircleCmd_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveCircleCmd_Request() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveCircleCmd_Response() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__MoveCircleCmd_Response__init(msg: *mut MoveCircleCmd_Response) -> bool;
    fn roarm_msgs__srv__MoveCircleCmd_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveCircleCmd_Response>, size: usize) -> bool;
    fn roarm_msgs__srv__MoveCircleCmd_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveCircleCmd_Response>);
    fn roarm_msgs__srv__MoveCircleCmd_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveCircleCmd_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveCircleCmd_Response>) -> bool;
}

// Corresponds to roarm_msgs__srv__MoveCircleCmd_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveCircleCmd_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

}



impl Default for MoveCircleCmd_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__MoveCircleCmd_Response__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__MoveCircleCmd_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveCircleCmd_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveCircleCmd_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveCircleCmd_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveCircleCmd_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveCircleCmd_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveCircleCmd_Response where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/MoveCircleCmd_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveCircleCmd_Response() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveLineCmd_Request() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__MoveLineCmd_Request__init(msg: *mut MoveLineCmd_Request) -> bool;
    fn roarm_msgs__srv__MoveLineCmd_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveLineCmd_Request>, size: usize) -> bool;
    fn roarm_msgs__srv__MoveLineCmd_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveLineCmd_Request>);
    fn roarm_msgs__srv__MoveLineCmd_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveLineCmd_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveLineCmd_Request>) -> bool;
}

// Corresponds to roarm_msgs__srv__MoveLineCmd_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveLineCmd_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f64,

}



impl Default for MoveLineCmd_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__MoveLineCmd_Request__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__MoveLineCmd_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveLineCmd_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveLineCmd_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveLineCmd_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveLineCmd_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveLineCmd_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveLineCmd_Request where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/MoveLineCmd_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveLineCmd_Request() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveLineCmd_Response() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__MoveLineCmd_Response__init(msg: *mut MoveLineCmd_Response) -> bool;
    fn roarm_msgs__srv__MoveLineCmd_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MoveLineCmd_Response>, size: usize) -> bool;
    fn roarm_msgs__srv__MoveLineCmd_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MoveLineCmd_Response>);
    fn roarm_msgs__srv__MoveLineCmd_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MoveLineCmd_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MoveLineCmd_Response>) -> bool;
}

// Corresponds to roarm_msgs__srv__MoveLineCmd_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveLineCmd_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

}



impl Default for MoveLineCmd_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__MoveLineCmd_Response__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__MoveLineCmd_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MoveLineCmd_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveLineCmd_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveLineCmd_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__MoveLineCmd_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MoveLineCmd_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MoveLineCmd_Response where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/MoveLineCmd_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__MoveLineCmd_Response() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__ServoCommandType_Request() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__ServoCommandType_Request__init(msg: *mut ServoCommandType_Request) -> bool;
    fn roarm_msgs__srv__ServoCommandType_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServoCommandType_Request>, size: usize) -> bool;
    fn roarm_msgs__srv__ServoCommandType_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServoCommandType_Request>);
    fn roarm_msgs__srv__ServoCommandType_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServoCommandType_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ServoCommandType_Request>) -> bool;
}

// Corresponds to roarm_msgs__srv__ServoCommandType_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServoCommandType_Request {
    /// Request Field
    pub command_type: i8,

}

impl ServoCommandType_Request {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const JOINT_JOG: i8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const TWIST: i8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const POSE: i8 = 2;

}


impl Default for ServoCommandType_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__ServoCommandType_Request__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__ServoCommandType_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServoCommandType_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__ServoCommandType_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__ServoCommandType_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__ServoCommandType_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServoCommandType_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServoCommandType_Request where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/ServoCommandType_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__ServoCommandType_Request() }
  }
}


#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__ServoCommandType_Response() -> *const std::ffi::c_void;
}

#[link(name = "roarm_msgs__rosidl_generator_c")]
extern "C" {
    fn roarm_msgs__srv__ServoCommandType_Response__init(msg: *mut ServoCommandType_Response) -> bool;
    fn roarm_msgs__srv__ServoCommandType_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServoCommandType_Response>, size: usize) -> bool;
    fn roarm_msgs__srv__ServoCommandType_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServoCommandType_Response>);
    fn roarm_msgs__srv__ServoCommandType_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServoCommandType_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ServoCommandType_Response>) -> bool;
}

// Corresponds to roarm_msgs__srv__ServoCommandType_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServoCommandType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

}



impl Default for ServoCommandType_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !roarm_msgs__srv__ServoCommandType_Response__init(&mut msg as *mut _) {
        panic!("Call to roarm_msgs__srv__ServoCommandType_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServoCommandType_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__ServoCommandType_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__ServoCommandType_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { roarm_msgs__srv__ServoCommandType_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServoCommandType_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServoCommandType_Response where Self: Sized {
  const TYPE_NAME: &'static str = "roarm_msgs/srv/ServoCommandType_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__roarm_msgs__srv__ServoCommandType_Response() }
  }
}






#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__GetPoseCmd() -> *const std::ffi::c_void;
}

// Corresponds to roarm_msgs__srv__GetPoseCmd
#[allow(missing_docs, non_camel_case_types)]
pub struct GetPoseCmd;

impl rosidl_runtime_rs::Service for GetPoseCmd {
    type Request = GetPoseCmd_Request;
    type Response = GetPoseCmd_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__GetPoseCmd() }
    }
}




#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__MoveJointCmd() -> *const std::ffi::c_void;
}

// Corresponds to roarm_msgs__srv__MoveJointCmd
#[allow(missing_docs, non_camel_case_types)]
pub struct MoveJointCmd;

impl rosidl_runtime_rs::Service for MoveJointCmd {
    type Request = MoveJointCmd_Request;
    type Response = MoveJointCmd_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__MoveJointCmd() }
    }
}




#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__MoveCircleCmd() -> *const std::ffi::c_void;
}

// Corresponds to roarm_msgs__srv__MoveCircleCmd
#[allow(missing_docs, non_camel_case_types)]
pub struct MoveCircleCmd;

impl rosidl_runtime_rs::Service for MoveCircleCmd {
    type Request = MoveCircleCmd_Request;
    type Response = MoveCircleCmd_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__MoveCircleCmd() }
    }
}




#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__MoveLineCmd() -> *const std::ffi::c_void;
}

// Corresponds to roarm_msgs__srv__MoveLineCmd
#[allow(missing_docs, non_camel_case_types)]
pub struct MoveLineCmd;

impl rosidl_runtime_rs::Service for MoveLineCmd {
    type Request = MoveLineCmd_Request;
    type Response = MoveLineCmd_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__MoveLineCmd() }
    }
}




#[link(name = "roarm_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__ServoCommandType() -> *const std::ffi::c_void;
}

// Corresponds to roarm_msgs__srv__ServoCommandType
#[allow(missing_docs, non_camel_case_types)]
pub struct ServoCommandType;

impl rosidl_runtime_rs::Service for ServoCommandType {
    type Request = ServoCommandType_Request;
    type Response = ServoCommandType_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__roarm_msgs__srv__ServoCommandType() }
    }
}


