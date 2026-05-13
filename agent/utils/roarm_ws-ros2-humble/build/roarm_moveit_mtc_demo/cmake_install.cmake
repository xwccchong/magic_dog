# Install script for directory: /workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_main/roarm_moveit_mtc_demo

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/workspace/roarm_ws/roarm_ws-ros2-humble/install/roarm_moveit_mtc_demo")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/llvm-objdump-18")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libroarm_moveit_mtc_demo_pick_place_task.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libroarm_moveit_mtc_demo_pick_place_task.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libroarm_moveit_mtc_demo_pick_place_task.so"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE SHARED_LIBRARY FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/libroarm_moveit_mtc_demo_pick_place_task.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libroarm_moveit_mtc_demo_pick_place_task.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libroarm_moveit_mtc_demo_pick_place_task.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libroarm_moveit_mtc_demo_pick_place_task.so"
         OLD_RPATH "/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_core/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/rviz_marker_tools/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_msgs/lib:/opt/ros/humble/lib:/opt/ros/humble/lib/aarch64-linux-gnu:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-18" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/libroarm_moveit_mtc_demo_pick_place_task.so")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo" TYPE EXECUTABLE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/cartesian")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian"
         OLD_RPATH "/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_core/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/rviz_marker_tools/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_msgs/lib:/opt/ros/humble/lib:/opt/ros/humble/lib/aarch64-linux-gnu:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-18" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian_modular" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian_modular")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian_modular"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo" TYPE EXECUTABLE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/cartesian_modular")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian_modular" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian_modular")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian_modular"
         OLD_RPATH "/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_core/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/rviz_marker_tools/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_msgs/lib:/opt/ros/humble/lib:/opt/ros/humble/lib/aarch64-linux-gnu:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-18" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/cartesian_modular")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/include/roarm_moveit_mtc_demo")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/pick_place" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/pick_place")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/pick_place"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo" TYPE EXECUTABLE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/pick_place")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/pick_place" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/pick_place")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/pick_place"
         OLD_RPATH "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo:/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_core/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/rviz_marker_tools/lib:/workspace/roarm_ws/roarm_ws-ros2-humble/install/moveit_task_constructor_msgs/lib:/opt/ros/humble/lib:/opt/ros/humble/lib/aarch64-linux-gnu:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-18" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/roarm_moveit_mtc_demo/pick_place")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo" TYPE DIRECTORY FILES
    "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_main/roarm_moveit_mtc_demo/launch"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_main/roarm_moveit_mtc_demo/config"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_main/roarm_moveit_mtc_demo/rviz"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/package_run_dependencies" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_index/share/ament_index/resource_index/package_run_dependencies/roarm_moveit_mtc_demo")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/parent_prefix_path" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_index/share/ament_index/resource_index/parent_prefix_path/roarm_moveit_mtc_demo")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo/environment" TYPE FILE FILES "/opt/ros/humble/share/ament_cmake_core/cmake/environment_hooks/environment/ament_prefix_path.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo/environment" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_environment_hooks/ament_prefix_path.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo/environment" TYPE FILE FILES "/opt/ros/humble/share/ament_cmake_core/cmake/environment_hooks/environment/path.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo/environment" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_environment_hooks/path.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_environment_hooks/local_setup.bash")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_environment_hooks/local_setup.sh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_environment_hooks/local_setup.zsh")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_environment_hooks/local_setup.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_environment_hooks/package.dsv")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/packages" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_index/share/ament_index/resource_index/packages/roarm_moveit_mtc_demo")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo/cmake" TYPE FILE FILES
    "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_core/roarm_moveit_mtc_demoConfig.cmake"
    "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/ament_cmake_core/roarm_moveit_mtc_demoConfig-version.cmake"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/roarm_moveit_mtc_demo" TYPE FILE FILES "/workspace/roarm_ws/roarm_ws-ros2-humble/src/roarm_main/roarm_moveit_mtc_demo/package.xml")
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/workspace/roarm_ws/roarm_ws-ros2-humble/build/roarm_moveit_mtc_demo/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
