# generated from rosidl_generator_py/resource/_idl.py.em
# with input from roarm_msgs:srv/MoveCircleCmd.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_MoveCircleCmd_Request(type):
    """Metaclass of message 'MoveCircleCmd_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('roarm_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'roarm_msgs.srv.MoveCircleCmd_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__move_circle_cmd__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__move_circle_cmd__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__move_circle_cmd__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__move_circle_cmd__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__move_circle_cmd__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class MoveCircleCmd_Request(metaclass=Metaclass_MoveCircleCmd_Request):
    """Message class 'MoveCircleCmd_Request'."""

    __slots__ = [
        '_x0',
        '_y0',
        '_z0',
        '_x1',
        '_y1',
        '_z1',
    ]

    _fields_and_field_types = {
        'x0': 'double',
        'y0': 'double',
        'z0': 'double',
        'x1': 'double',
        'y1': 'double',
        'z1': 'double',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.x0 = kwargs.get('x0', float())
        self.y0 = kwargs.get('y0', float())
        self.z0 = kwargs.get('z0', float())
        self.x1 = kwargs.get('x1', float())
        self.y1 = kwargs.get('y1', float())
        self.z1 = kwargs.get('z1', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.x0 != other.x0:
            return False
        if self.y0 != other.y0:
            return False
        if self.z0 != other.z0:
            return False
        if self.x1 != other.x1:
            return False
        if self.y1 != other.y1:
            return False
        if self.z1 != other.z1:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def x0(self):
        """Message field 'x0'."""
        return self._x0

    @x0.setter
    def x0(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'x0' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'x0' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._x0 = value

    @builtins.property
    def y0(self):
        """Message field 'y0'."""
        return self._y0

    @y0.setter
    def y0(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'y0' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'y0' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._y0 = value

    @builtins.property
    def z0(self):
        """Message field 'z0'."""
        return self._z0

    @z0.setter
    def z0(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'z0' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'z0' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._z0 = value

    @builtins.property
    def x1(self):
        """Message field 'x1'."""
        return self._x1

    @x1.setter
    def x1(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'x1' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'x1' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._x1 = value

    @builtins.property
    def y1(self):
        """Message field 'y1'."""
        return self._y1

    @y1.setter
    def y1(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'y1' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'y1' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._y1 = value

    @builtins.property
    def z1(self):
        """Message field 'z1'."""
        return self._z1

    @z1.setter
    def z1(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'z1' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'z1' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._z1 = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_MoveCircleCmd_Response(type):
    """Metaclass of message 'MoveCircleCmd_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('roarm_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'roarm_msgs.srv.MoveCircleCmd_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__move_circle_cmd__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__move_circle_cmd__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__move_circle_cmd__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__move_circle_cmd__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__move_circle_cmd__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class MoveCircleCmd_Response(metaclass=Metaclass_MoveCircleCmd_Response):
    """Message class 'MoveCircleCmd_Response'."""

    __slots__ = [
        '_success',
        '_message',
    ]

    _fields_and_field_types = {
        'success': 'boolean',
        'message': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', bool())
        self.message = kwargs.get('message', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.success != other.success:
            return False
        if self.message != other.message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'success' field must be of type 'bool'"
        self._success = value

    @builtins.property
    def message(self):
        """Message field 'message'."""
        return self._message

    @message.setter
    def message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'message' field must be of type 'str'"
        self._message = value


class Metaclass_MoveCircleCmd(type):
    """Metaclass of service 'MoveCircleCmd'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('roarm_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'roarm_msgs.srv.MoveCircleCmd')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__move_circle_cmd

            from roarm_msgs.srv import _move_circle_cmd
            if _move_circle_cmd.Metaclass_MoveCircleCmd_Request._TYPE_SUPPORT is None:
                _move_circle_cmd.Metaclass_MoveCircleCmd_Request.__import_type_support__()
            if _move_circle_cmd.Metaclass_MoveCircleCmd_Response._TYPE_SUPPORT is None:
                _move_circle_cmd.Metaclass_MoveCircleCmd_Response.__import_type_support__()


class MoveCircleCmd(metaclass=Metaclass_MoveCircleCmd):
    from roarm_msgs.srv._move_circle_cmd import MoveCircleCmd_Request as Request
    from roarm_msgs.srv._move_circle_cmd import MoveCircleCmd_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
