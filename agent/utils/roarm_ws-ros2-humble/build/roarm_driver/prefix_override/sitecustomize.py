import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/workspace/roarm_ws/roarm_ws-ros2-humble/install/roarm_driver'
