cd /workspace/roarm_ws/roarm_ws-ros2-humble
colcon build --packages-select roarm_msgs 
colcon build --packages-select moveit_servo 
colcon build --packages-select rviz_marker_tools 
colcon build --packages-select moveit_task_constructor_msgs 
colcon build --packages-select moveit_task_constructor_core 
colcon build --packages-select moveit_task_constructor_capabilities 
colcon build --packages-select moveit_task_constructor_visualization 
colcon build --packages-select roarm_moveit_cmd 
colcon build --packages-select roarm_moveit_ikfast_plugins 
colcon build --packages-select roarm_moveit_mtc_demo 
colcon build --packages-select roarm_moveit_servo 
colcon build --packages-select roarm_description roarm_driver roarm_moveit --symlink-install 
# 2. 将工作空间的 setup.zsh 写入 Zsh 配置文件（注意路径是 /workspace/...）
echo "source /workspace/roarm_ws/roarm_ws-ros2-humble/install/setup.zsh" >> ~/.zshrc
# 3. 立即刷新当前环境
source ~/.zshrc
