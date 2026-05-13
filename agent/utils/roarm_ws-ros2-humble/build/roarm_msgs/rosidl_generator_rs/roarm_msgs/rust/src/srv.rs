#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to roarm_msgs__srv__GetPoseCmd_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetPoseCmd_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetPoseCmd_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetPoseCmd_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetPoseCmd_Request {
  type RmwMsg = super::srv::rmw::GetPoseCmd_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to roarm_msgs__srv__GetPoseCmd_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetPoseCmd_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetPoseCmd_Response {
  type RmwMsg = super::srv::rmw::GetPoseCmd_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        x: msg.x,
        y: msg.y,
        z: msg.z,
        roll: msg.roll,
        pitch: msg.pitch,
        yaw: msg.yaw,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      roll: msg.roll,
      pitch: msg.pitch,
      yaw: msg.yaw,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      roll: msg.roll,
      pitch: msg.pitch,
      yaw: msg.yaw,
    }
  }
}


// Corresponds to roarm_msgs__srv__MoveJointCmd_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveJointCmd_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MoveJointCmd_Request {
  type RmwMsg = super::srv::rmw::MoveJointCmd_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        x: msg.x,
        y: msg.y,
        z: msg.z,
        roll: msg.roll,
        pitch: msg.pitch,
        yaw: msg.yaw,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      roll: msg.roll,
      pitch: msg.pitch,
      yaw: msg.yaw,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      roll: msg.roll,
      pitch: msg.pitch,
      yaw: msg.yaw,
    }
  }
}


// Corresponds to roarm_msgs__srv__MoveJointCmd_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveJointCmd_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,

}



impl Default for MoveJointCmd_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveJointCmd_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MoveJointCmd_Response {
  type RmwMsg = super::srv::rmw::MoveJointCmd_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
    }
  }
}


// Corresponds to roarm_msgs__srv__MoveCircleCmd_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveCircleCmd_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MoveCircleCmd_Request {
  type RmwMsg = super::srv::rmw::MoveCircleCmd_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        x0: msg.x0,
        y0: msg.y0,
        z0: msg.z0,
        x1: msg.x1,
        y1: msg.y1,
        z1: msg.z1,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      x0: msg.x0,
      y0: msg.y0,
      z0: msg.z0,
      x1: msg.x1,
      y1: msg.y1,
      z1: msg.z1,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      x0: msg.x0,
      y0: msg.y0,
      z0: msg.z0,
      x1: msg.x1,
      y1: msg.y1,
      z1: msg.z1,
    }
  }
}


// Corresponds to roarm_msgs__srv__MoveCircleCmd_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveCircleCmd_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,

}



impl Default for MoveCircleCmd_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveCircleCmd_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MoveCircleCmd_Response {
  type RmwMsg = super::srv::rmw::MoveCircleCmd_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
    }
  }
}


// Corresponds to roarm_msgs__srv__MoveLineCmd_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveLineCmd_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MoveLineCmd_Request {
  type RmwMsg = super::srv::rmw::MoveLineCmd_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        x: msg.x,
        y: msg.y,
        z: msg.z,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      x: msg.x,
      y: msg.y,
      z: msg.z,
    }
  }
}


// Corresponds to roarm_msgs__srv__MoveLineCmd_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MoveLineCmd_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,

}



impl Default for MoveLineCmd_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MoveLineCmd_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MoveLineCmd_Response {
  type RmwMsg = super::srv::rmw::MoveLineCmd_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
    }
  }
}


// Corresponds to roarm_msgs__srv__ServoCommandType_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServoCommandType_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ServoCommandType_Request {
  type RmwMsg = super::srv::rmw::ServoCommandType_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        command_type: msg.command_type,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      command_type: msg.command_type,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      command_type: msg.command_type,
    }
  }
}


// Corresponds to roarm_msgs__srv__ServoCommandType_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServoCommandType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,

}



impl Default for ServoCommandType_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServoCommandType_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ServoCommandType_Response {
  type RmwMsg = super::srv::rmw::ServoCommandType_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
    }
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


