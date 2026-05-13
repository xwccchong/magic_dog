#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to roarm_msgs__msg__ServoStatus
/// Message

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServoStatus {
    /// will contains integer code
    pub code: i8,

    /// will contain explanatory message
    pub message: std::string::String,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ServoStatus::default())
  }
}

impl rosidl_runtime_rs::Message for ServoStatus {
  type RmwMsg = super::msg::rmw::ServoStatus;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        code: msg.code,
        message: msg.message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      code: msg.code,
        message: msg.message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      code: msg.code,
      message: msg.message.to_string(),
    }
  }
}


